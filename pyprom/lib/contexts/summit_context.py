"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from .feature_context import FeatureContext
from .exceptions import LinkageException

class SummitContext(FeatureContext):

    def __init__(self, manager, summit, saddles, neighbor_summits, id=None, disabled=False):
        """
        A SummitContext.
        """
        super().__init__(summit, manager, id=id, disabled=disabled)
        self._saddles = saddles
        self._saddles_lookup = {x.id:x for x in saddles}
        self._neighbor_summits = neighbor_summits


    @property
    def summit(self):
        """
        summit is immutable.
        :return:
        """
        return self._feature

    @property
    def saddles(self):
        return self._saddles

    @property
    def neighbor_summits(self):
        return self._neighbor_summits

    def feature_neighbors(self):
        """
        Returns our directly connected neighbors, in this case, our Saddles.
        :return:
        """
        if not self.disabled:
            return self._saddles


    def _add_saddle(self, saddle):
        """
        Adds Saddle to this context. In effect, this links this Saddle to that Summit
        --
        This makes no effort to change any states on the manager and therefore should
        only be called from the manager.

        :param saddle: Saddle
        :return: bool if added
        """
        if not self._saddles_lookup.get(saddle.id):
            self._saddles.append(saddle)
            self._saddles_lookup[saddle.id] = saddle
            return True
        return False

    def _remove_saddle(self, saddle):
        """
        Removes Saddle from this context. In effect, this unlinks this Saddle from that Summit
        --
        This makes no effort to change any states on the manager and therefore should
        only be called from the manager.

        :param saddle: Saddle
        :return: bool indicating if removed
        """
        if self._saddles_lookup.get(saddle.id):
            self._saddles.remove(saddle)
            del self._saddles_lookup[saddle.id]
            return True
        return False

    def link_saddle(self, saddle, disable_duplicate=True):
        """
        Link a Saddle to this Summit.
        Both Saddle and Summit must be tracked by context manager or this will fail.
        :param saddle: Saddle to link.
        :return bool, bool: Success, duplicate
        """

        # Raises Exception if saddle or summit isn't in the context.
        added_saddle, added_summit, recorded_saddle, recorded_summit, duplicate\
            = self.manager.link_saddle_summit(saddle, self.summit, disable_duplicate)

        if duplicate:
            # if this is a duplicate, then success means we added nothing.
            return not (added_saddle or added_summit or recorded_saddle or recorded_summit), duplicate

        # Bool for everything added (Success indicator), bool for duplicate.
        return (added_saddle and added_summit and recorded_saddle and recorded_summit), duplicate

    def remove_saddle(self, saddle):
        """
        UnLink a Saddle to this Summit.
        Both Saddle and Summit must be tracked by context manager or this will fail.
        :param saddle: Saddle to link.
        :return bool: Success indicator
        """

        # Raises Exception if saddle or summit isn't in the context.
        return self.manager.delink_saddle_summit(saddle, self.summit)

    def __repr__(self):
        return f"<SummitContext> {self.summit}: {len(self.saddles)} Saddles"



