"""
pyProm: Copyright 2016

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

Base object for locations includes logging
"""
import logging


class _Base(object):
    """
    Very Base object, which contains just a logger.
    """
    def __init__(self):
        self.logger = logging.getLogger('pyProm.{}'.format(__name__))
