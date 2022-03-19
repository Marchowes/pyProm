"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from .feature_context import FeatureContext
from .exceptions import LinkageException

class SaddleContext(FeatureContext):

    def __init__(self, manager, saddle, summits, neighbor_saddles, id=None, disabled=False):
        """
        A SummitContext.
        """
        super().__init__(saddle, manager, id=id, disabled=disabled)
        self._summits = summits
        self._summits_lookup = {x.id:x for x in summits}
        self._neighbor_saddles = neighbor_saddles

    @property
    def summits(self):
        return self._summits

    @property
    def saddle(self):
        """
        saddle is immutable.
        :return:
        """
        return self._feature

    @property
    def neighbor_saddles(self):
        return self._neighbor_saddles

    def _add_summit(self, summit):
        """
        Adds Summit to this context. In effect, this links that Summit to that Saddle.
        --
        This makes no effort to change any states on the manager and therefore should
        only be called from the manager.

        :param summit: Summit
        :return: bool indicating if successful
        """
        if not self._summits_lookup.get(summit.id):
            self._summits.append(summit)
            self._summits_lookup[summit.id] = summit
            return True
        return False

    def _remove_summit(self, summit):
        """
        Removes Summit from this context. In effect, this unlinks a Summit from this Saddle.
        --
        This makes no effort to change any states on the manager and therefore should
        only be called from the manager.

        :param summit: Summit
        :return: bool indicating if successful
        """
        if self._summits_lookup.get(summit.id):
            self._summits.remove(summit)
            del self._summits_lookup[summit.id]
            return True
        return False

    def link_summit(self, summit, disable_duplicate=True):
        """
        Link a Summit to this Saddle.
        Both Saddle and Summit must be tracked by context manager or this will fail.
        :param summit: Summit to link.
        :return bool, bool: Success, duplicate
        """

        # Raises Exception if saddle or summit isn't in the context.
        added_saddle, added_summit, recorded_saddle, recorded_summit, duplicate\
            = self.manager.link_saddle_summit(self.saddle, summit, disable_duplicate)

        if duplicate:
            # if this is a duplicate, then success means we added nothing.
            return not (added_saddle or added_summit or recorded_saddle or recorded_summit), duplicate

        # Bool for everything added (Success indicator), bool for duplicate.
        return (added_saddle and added_summit and recorded_saddle and recorded_summit), duplicate

    def remove_summit(self, summit):
        """
        UnLink a Summit from this Saddle
        Both Saddle and Summit must be tracked by context manager or this will fail.
        :param summit: Summit to de-link
        :return bool: Success indicator
        """

        # Raises Exception if saddle or summit isn't in the context.
        return self.manager.delink_saddle_summit(self.saddle, summit)

    def feature_neighbors(self):
        """
        Returns our directly connected non disabled neighbors, in this case, our Summits.
        :return:
        """
        if not self.disabled:
            return self._summits

    # @classmethod
    # def from_dict_and_attach(cls, saddle_context_dict, manager):
    #     """
    #     Create this object from dictionary representation.
    #
    #     This function requires a saddle/summit lookup dict
    #     in order to create the correct associations.
    #     Therefore those saddles/summits must already exist
    #     in memory for this to work.
    #
    #     :param saddle_context_dict: dict representation of this object.
    #     :param saddle_lookup: {id: Saddle} lookup dict.
    #     :param summit_lookup: {id: Summit} lookup dict.
    #     :return: a new SaddleContext object.
    #     :rtype: :class:`SaddleContext`
    #     """
    #
    #     #  manager, saddle, summits, neighbor_saddles
    #
    #     return cls(manager)
    #
    # def to_dict(self):
    #     """
    #     Produces a dictionary of this object. uses feature IDs.
    #     :return: dict representation of this object.
    #     """
    #     to_dict = {
    #         'summits': [x.id for x in self.summits],
    #         'saddle': self.saddle.id,
    #         'id': self.id,
    #         'disabled': self.disabled,
    #     }
    #     return to_dict

    def __repr__(self):
        return f"<SaddleContext> {self.saddle}: {len(self.summits)} Summits"
