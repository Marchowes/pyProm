"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.
"""

class SaddleContextException(Exception):
    pass

class SummitContextException(Exception):
    pass

class LinkageException(Exception):

    def __init__(self, added_saddle, added_summit, recorded_saddle, recorded_summit, duplicate):
        self.added_saddle = added_saddle
        self.added_summit = added_summit
        self.recorded_saddle = recorded_saddle
        self.recorded_summit = recorded_summit
        self.duplicate = duplicate
        msg = lambda x: f"{'OK' if x else 'FAILED'},"
        super().__init__(f"added_saddle: {msg(self.added_saddle)} added_summit: {msg(self.added_summit)} recorded_saddle: {msg(self.recorded_saddle)} recorded_summit: {msg(self.recorded_summit)} duplicate: {self.duplicate}")



