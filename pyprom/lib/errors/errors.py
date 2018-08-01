"""
pyProm: Copyright 2018.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a base container class for storing GridPoint
type location objects.
"""


class NoLinkersError(Exception):
    """
    Raised when the expected action expects linkers to exist. Usually
    this means walk was not executed.
    """

    pass
