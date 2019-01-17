"""
pyProm: Copyright 2016.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

Base object for containers includes logging
"""
import logging


class _Base:
    """
    Very Base object for containers, which contains just a logger.
    """

    def __init__(self):
        """
        Base initialization of Container Object.
        """
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
