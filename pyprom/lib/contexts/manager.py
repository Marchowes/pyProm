"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from collections import defaultdict

from .saddle_context import SaddleContext
from .summit_context import SummitContext
from .exceptions import SummitContextException, SaddleContextException
from ..containers.saddles import SaddlesContainer
from ..locations.runoff import Runoff
from ..util import randomString

class FeatureContextManager:

    def __init__(self, summits, saddles, runoffs, *args, **kwargs):
        """
        a feature context creates a context for all first class features
        (Saddles, Summits, Runoffs). This context controls whether those features
        have certain parameters, like if they are disabled, or what neighbors they have.

        :param summits: list of Summits
        :param saddles: list of Saddles
        :param runoffs: list of Runoffs
        :param args:
        :param kwargs:
        """

        self.id = kwargs.get('id')
        if not self.id:
            self.id = randomString()

        self._saddles = []
        self._summits = []
        self.summit_lookup = {}
        self.saddle_lookup = {}

        for s in summits:
            self.add_summit(s)
        for s in saddles:
            self.add_saddle(s)
        for r in runoffs:
            self.add_saddle(r)

        self.disabled_tracker = {}
        self.basin_saddle_tracker = defaultdict(list)

        self.saddle_to_summit_tracker = defaultdict(dict) # {'saddle.id': {summit.id: bool, ...}}
        self.summit_to_saddle_tracker = defaultdict(dict)

    def get_ctx(self, feature):
        """
        Returns feature context on remote object corresponding to this Context Manager.
        :param feature: Saddle, Summit, Runoff
        :return: SaddleContext, SummitContext
        """
        return feature.contexts.get(self.id, None)

    def add_summit(self, summit, disabled=False):
        """
        Add a Summit to this context.
        :param summit: Summit
        """
        added = self._add_feature(summit, self.summit_lookup, self._summits, disabled=disabled)
        if added:
            sc = SummitContext(self, summit, [], [], disabled=disabled)
            summit.contexts[self.id] = sc
        return added

    @property
    def summits(self):
        """
        List of all summits.
        """
        return self._summits

    def add_saddle(self, saddle, disabled=False):
        """
        Add a Saddle to this context.
        :param saddle: Saddle/Runoff
        """
        added = self._add_feature(saddle, self.saddle_lookup, self._saddles, disabled=disabled)
        if added:
            sc = SaddleContext(self, saddle, [], [], disabled=disabled)
            saddle.contexts[self.id] = sc
        return added

    @property
    def saddles_exact(self):
        """
        list of all explicit saddle objects.
        """
        return [x for x in self._saddles if not isinstance(x, Runoff)]

    @property
    def saddles(self):
        """
        list of saddles/runoffs
        """
        return self._saddles

    @property
    def runoffs(self):
        """
        List of Runoffs
        """
        return [x for x in self._saddles if isinstance(x, Runoff)]


    def link_saddle_summit(self, saddle, summit, disable_duplicate=True):
        """
        Links tracks Saddles/Summits. Note that disabled
        Saddles/Summit/Runoffs can still be linked.
        :param saddle: Saddle/Runoff
        :param summit: Summit
        :param disable_duplicate: bool. if 1 saddle links to 1 summit > 1 times,
         disable saddle.
        :return bool, bool, bool, bool, bool: added_saddle, added_summit,
         recorded_saddle, recorded_summit, purged_duplicate.
        """

        if not self.saddle_lookup.get(saddle.id):
            raise SaddleContextException(f"Couldn't find Saddle {saddle.id} in this context.")
        if not self.summit_lookup.get(summit.id):
            raise SummitContextException(f"Couldn't find Summit {summit.id} in this context.")

        # Update manager records.
        recorded_saddle, recorded_summit, duplicate = self.record_saddle_summit_linkage(saddle, summit)

        if duplicate and disable_duplicate:
            # de-link
            a, b = self.record_saddle_summit_delinkage(saddle, summit)
            # reach into feature contexts and remove pairing.
            self.get_ctx(saddle)._remove_summit(summit)
            self.get_ctx(summit)._remove_saddle(saddle)
            # disable that saddle.
            self.disable_feature(saddle)
            return False, False, False, False, True

        # reach into feature contexts and update.
        added_saddle = self.get_ctx(saddle)._add_summit(summit)
        added_summit = self.get_ctx(summit)._add_saddle(saddle)

        return added_saddle, added_summit, recorded_saddle, recorded_summit, duplicate

    def delink_saddle_summit(self, saddle, summit):
        """
        Delinks tracked Saddles/Summits
        :param saddle: Saddle/Runoff
        :param summit: Summit
        :return: bool saddle, bool summit
        """

        if not self.saddle_lookup[saddle.id]:
            raise SaddleContextException("Couldn't find Saddle {saddle.id} in this context.")
        if not self.summit_lookup[summit.id]:
            raise SummitContextException("Couldn't find Summit {summit.id} in this context.")

        # reach into feature contexts and update.
        self.get_ctx(saddle)._remove_summit(summit)
        self.get_ctx(summit)._remove_saddle(saddle)

        # Update manager records.
        dedsaddle, dedsummit = self.record_saddle_summit_delinkage(saddle, summit)
        if not dedsaddle and dedsummit:
            return False
        return True

    def check_linkage_trackers(self, saddle_id, summit_id):
        """
        Checks internal tracker object for saddle/summit linkage.

        :param saddle_id: Saddle id
        :param summit_id: Summit id
        :return bool, bool: Saddle tracker OK, Summit tracker OK
        """
        return (self.saddle_to_summit_tracker[saddle_id].get(summit_id, False),
               self.summit_to_saddle_tracker[summit_id].get(saddle_id, False))

    def record_saddle_summit_linkage(self, saddle, summit):
        """
        Records the linkage between a saddle and a summit in the context manager.
        Local tracking must be handled by the caller.
        :param saddle: Saddle/Runoff
        :param summit: Summit
        :returns bool, bool, bool: Bool if added saddle, Bool if added summit, Bool if duplicate
        """
        added_saddle = False
        added_summit = False

        saddle_tracker_exist, summit_tracker_exist =\
            self.check_linkage_trackers(saddle.id, summit.id)

        # if this saddle-summit is already linked, we have a duplicate. Report it as such.
        if saddle_tracker_exist and summit_tracker_exist:
            return False, False, True

        if not saddle_tracker_exist:
            self.saddle_to_summit_tracker[saddle.id][summit.id] = True
            added_summit = True
        if not summit_tracker_exist:
            self.summit_to_saddle_tracker[summit.id][saddle.id] = True
            added_saddle = True
        return added_saddle, added_summit, False

    def record_saddle_summit_delinkage(self, saddle, summit):
        """
        Unrecords the linkage between a saddle and a summit in the context manager.
        Local tracking must be handled by the caller.
        :param saddle: Saddle/Runoff
        :param summit: Summit
        :returns: Bool if removed saddle, Bool if removed summit
        """
        removed_saddle = False
        removed_summit = False
        saddle_tracker_exist, summit_tracker_exist =\
            self.check_linkage_trackers(saddle.id, summit.id)

        if saddle_tracker_exist:
            del self.saddle_to_summit_tracker[saddle.id][summit.id]
            removed_summit = True
        if summit_tracker_exist:
            del self.summit_to_saddle_tracker[summit.id][saddle.id]
            removed_saddle = True
        return removed_saddle, removed_summit

    def remove_summit(self, summit):
        """
        Remove a Summit from this context. Cleans up remote SummitContexts as well.
        :param summit: Summit
        """
        # de-link summit from any saddles.
        if self.summit_to_saddle_tracker[summit.id]:
            for saddle_id in self.summit_to_saddle_tracker[summit.id].keys():
                self.delink_saddle_summit(self.saddle_lookup[saddle_id], summit)
        # remove from disabled tracker if it exists.
        if self.is_disabled(summit.id):
            del self.disabled_tracker[summit.id]
        # remove summit from lookup, list and the remote context.
        self._remove_feature(summit, self.summit_lookup, self._summits)

    def remove_saddle(self, saddle):
        """
        Remove a Saddle from this context. Cleans up remote SaddleContexts as well.
        :param saddle: Saddle
        """
        #de-link from any summits. Cleans up remote SaddleContexts as well.
        if self.saddle_to_summit_tracker[saddle.id]:
            for summit_id in self.saddle_to_summit_tracker[saddle.id].keys():
                self.delink_saddle_summit(saddle, self.summit_lookup[summit_id])
        # remove from disabled tracker if it exists.
        if self.is_disabled(saddle.id):
            del self.disabled_tracker[saddle.id]
        # remove saddle from lookup, list and the remote context.
        self._remove_feature(saddle, self.saddle_lookup, self._saddles)

    def disable_feature(self, feature):
        """
        Disables feature From Tracker and in Feature Context.
        :param feature: Saddle/Summit/Runoff object to disable
        """
        self.disabled_tracker[feature.id] = True
        self.get_ctx(feature)._disabled = True

    def enable_feature(self, feature):
        """
        Enables Feature in Tracker and in Feature Context.
        :param feature: Saddle/Summit/Runoff object to enable
        """
        if self.is_disabled(feature.id):
            del self.disabled_tracker[self.feature.id]
        self.get_ctx(feature)._disabled = False

    def is_disabled(self, feature_id):
        """
        See if a feature is disabled.
        :param feature_id: string ID of feature.
        :return: bool
        """
        return self.disabled_tracker.get(feature_id, False)

    def _populate_dicts(self, feature_list, destination_dict):
        """
        basic lookup population function
        """
        for feature in feature_list:
            destination_dict[feature.id] = feature
        return destination_dict

    def _add_feature(self, feature, feature_lookup, feature_list, disabled=False):
        """
        Adds the feature to the feature list item, and the lookup.
        this DOES NOT create the feature context on the feature itself. That burden
        is on the caller.

        :param feature:
        :param feature_lookup:
        :param feature_list:
        :param disabled:
        :return:
        """

        if not feature_lookup.get(feature.id):
            feature_list.append(feature)
            feature_lookup[feature.id] = feature
            if disabled:
                self.disabled_tracker[feature.id] = True
            return True
        return False

    def _remove_feature(self, feature, feature_lookup, feature_list):
        """
        Removes the feature from the feature list item, and the lookup.
        This DOES remove the context on the feature.

        :param feature:
        :param feature_lookup:
        :param feature_list:
        """
        if feature_lookup.get(feature.id):
            feature_list.remove(feature)
            del feature_lookup[feature.id]
            del feature.contexts[self.id]
            return True
        return False

    def to_dict(self):
        """
        :return: dict representation of this object.
        """
        to_dict = {
            'id': self.id,
            'summit_ids': [s.id for s in self._summits],
            'saddle_ids': [s.id for s in self._saddles],
            'disabled_tracker': self.disabled_tracker,
            'saddle_to_summit_tracker': self.saddle_to_summit_tracker
            #'basin_saddle_tracker': self.basin_saddle_tracker
        }
        return to_dict

    @classmethod
    def from_dict(cls, from_dict, saddle_container, summit_container, runoff_container):
        """
        :param from_dict:
        :param saddle_container:
        :param summit_container:
        :param runoff_container:
        :return:
        """

        combined_container = SaddlesContainer(saddle_container.points + runoff_container.points)

        id = from_dict['id']

        # build feature lists
        summits = [summit_container.by_id(summit_id) for summit_id in from_dict['summit_ids']]
        saddles = [combined_container.by_id(saddle_id) for saddle_id in from_dict['saddle_ids']]

        # build summit_to_saddle_tracker
        summit_to_saddle_tracker = defaultdict(dict)
        for saddle_id, summit_ids in from_dict['saddle_to_summit_tracker'].items():
            for summit_id, val in summit_ids.items():
                summit_to_saddle_tracker[summit_id][saddle_id] = val

        # basin_saddle_tracker = from_dict['basin_saddle_tracker']

        # this will build out contexts which will be disposed of.
        context = cls(summits, saddles, [], id=id)
        context.disabled_tracker = from_dict['disabled_tracker']

        # make sure this is a defaultdict.
        context.saddle_to_summit_tracker = defaultdict(dict)
        for sad, sum_dict in from_dict['saddle_to_summit_tracker'].items():
            context.saddle_to_summit_tracker[sad]=sum_dict

        context.summit_to_saddle_tracker = summit_to_saddle_tracker

        # rebuild our contexts.

        for saddle in context._saddles:
            saddle.contexts[context.id] = SaddleContext(context, saddle, [context.summit_lookup[sum] for sum, val in context.saddle_to_summit_tracker[saddle.id].items() if val], [], disabled=context.disabled_tracker.get(saddle.id, False))

        for summit in context._summits:
            summit.contexts[context.id] = SummitContext(context, summit, [context.saddle_lookup[sad] for sad, val in context.summit_to_saddle_tracker[summit.id].items() if val], [], disabled=context.disabled_tracker.get(summit.id, False))

        return context


    def __repr__(self):
        """
        :return: String representation of this object
        """
        return f"<FeatureContextManager> Summits:{len(self._summits)} " \
               f"Saddles:{len(self._saddles)}"