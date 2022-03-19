"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

from ..util import randomString

class FeatureContext:

    def __init__(self, feature, manager, id=None, disabled=False):
        """
        A Base Feature Context. Basically sets up id, disabled.
        """

        self.manager = manager
        self.id = id
        if not self.id:
            self.id = randomString()
        self._feature = feature
        self._disabled = disabled

    @property
    def disabled(self):
        return self._disabled

    def disable(self):
        """
        Disable this feature
        """
        self._disabled = True
        self.manager.disabled_tracker[self._feature.id] = True

    def enable(self):
        """
        Enable this feature
        """
        self._disabled = False
        if self.manager.disabled_tracker.get(self._feature.id):
            del self.manager.disabled_tracker[self._feature.id]
