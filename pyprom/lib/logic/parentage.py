"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for manipulating a pyProm Prominence Island
"""

from collections import deque


# Use static values as they are a bit more performant and we'll be using them a lot.
LOCAL_LINKER = 0
LOWEST_SADDLE = 1
HIGHEST_SUMMIT = 2

class ProminenceIslandParentFinder:

    def __init__(self, summit):
        self.summit = summit
        self.queue = deque()
        self.candidate_key_col = None
        self.candidate_parent = None

        self.candidate_offmap_saddles = set()


    def find_parent(self):
        for local_linker in self.summit.saddles:
            if local_linker.disqualified:
                continue
            # we pass a tuple around since it's lightweight and disposable.
            obj = (
                local_linker, # Linker between this summit and the next saddle.
                None, # lowest saddle seen
                None, # highest summit seen
            )
            self.queue.append(obj)
        self.breadth_search()

        offmap_saddles = []
        if self.candidate_key_col:
            for candidate_offmap_saddle in self.candidate_offmap_saddles:
                if candidate_offmap_saddle.elevation > self.candidate_key_col.elevation:
                    offmap_saddles.append(candidate_offmap_saddle)
        else:
            offmap_saddles = self.candidate_offmap_saddles

        return self.candidate_key_col, self.candidate_parent, offmap_saddles

    def breadth_search(self):
        """
        the breadth search function, consumes the current queue until exhausted.
        Its the responsibility of the caller to iterate and replenish the queue.
        """
        while self.queue:
            obj = self.queue.pop()
            saddle = obj[LOCAL_LINKER].saddle
            # This will fail if we encounter a runoff or some other oddball scenarios.
            ##############
            try:
                next_linker = obj[LOCAL_LINKER].linker_other_side_of_saddle()[0]
            except:
                # keep track of any low saddles that lead up to an edge.
                # We'll cull any invalid ones at the caller
                if saddle.edgeEffect:
                    if obj[LOWEST_SADDLE]:
                        self.candidate_offmap_saddles.add(obj[LOWEST_SADDLE])
                else:
                    print(f"BAD: {saddle}")
                continue
            #################
            summit_under_test = next_linker.summit

            if summit_under_test.edgeEffect:
                if obj[LOWEST_SADDLE]:
                    self.candidate_offmap_saddles.add(obj[LOWEST_SADDLE])


            # lowest seen already lower than the candidate? bail.
            if self.candidate_key_col and obj[LOWEST_SADDLE].elevation < self.candidate_key_col.elevation:
                continue

            # have we seen a highest summit, and are we at a lower saddle?
            if obj[HIGHEST_SUMMIT] and saddle.elevation < obj[LOWEST_SADDLE].elevation:
                if not self.candidate_key_col:
                    self.candidate_key_col = obj[LOWEST_SADDLE]
                    self.candidate_parent = obj[HIGHEST_SUMMIT]
                    continue

                # If we have an existing candidate col and we're the higher one, use us.
                if self.candidate_key_col and self.candidate_key_col.elevation < obj[LOWEST_SADDLE].elevation:
                    self.candidate_key_col = obj[LOWEST_SADDLE]
                    self.candidate_parent = obj[HIGHEST_SUMMIT]
                    continue

                # If we have an existing candidate col and we're the same height, use the one with the taller summit
                elif self.candidate_key_col and self.candidate_key_col.elevation == obj[LOWEST_SADDLE].elevation:
                    if self.candidate_parent.elevation < obj[HIGHEST_SUMMIT].elevation:
                        self.candidate_key_col = obj[LOWEST_SADDLE]
                        self.candidate_parent = obj[HIGHEST_SUMMIT]
                        continue

            #
            # add logic for handling map edges here.
            #

            # check for low saddle.
            if not obj[LOWEST_SADDLE]:
                lowest = saddle
            elif obj[LOWEST_SADDLE] and saddle.elevation < obj[LOWEST_SADDLE].elevation:
                lowest = saddle
            else:
                lowest = obj[LOWEST_SADDLE]

            # if we found a summit taller than anything we've seen, mark it.
            if obj[HIGHEST_SUMMIT] and summit_under_test.elevation > obj[HIGHEST_SUMMIT].elevation:
                highest = summit_under_test
            elif not obj[HIGHEST_SUMMIT] and summit_under_test.elevation > self.summit.elevation:
                highest = summit_under_test
            # otherwise pass along what we already have.
            else:
                highest = obj[HIGHEST_SUMMIT]

            # Alright, we're done here, queue up the next summits and add them to the next ring.
            for next_saddle_linker in summit_under_test.saddles:
                if next_saddle_linker.id == next_linker.id or next_saddle_linker.disqualified:
                    continue
                self.queue.appendleft((next_saddle_linker, lowest, highest))


####
"""
Troublesome scenarios: Equal height, 
Should we track equal heights along a path and use the low point between them as the col?

Edge, we need to track edges.
"""


class LineParentFinder:

    def __init__(self, summit):
        self.summit = summit
        self.queue = deque()
        self.candidate_key_col = None
        self.candidate_parent = None

        self.candidate_offmap_saddles = set()

    def find_parent(self):
        for local_linker in self.summit.saddles:
            if local_linker.disqualified:
                continue
            # we pass a tuple around since it's lightweight and disposable.
            obj = (
                local_linker,  # Linker between this summit and the next saddle.
                None,  # lowest saddle seen
            )
            self.queue.append(obj)
        self.breadth_search()

        offmap_saddles = []
        if self.candidate_key_col:
            for candidate_offmap_saddle in self.candidate_offmap_saddles:
                if candidate_offmap_saddle.elevation > self.candidate_key_col.elevation:
                    offmap_saddles.append(candidate_offmap_saddle)
        else:
            offmap_saddles = self.candidate_offmap_saddles

        return self.candidate_key_col, self.candidate_parent, offmap_saddles


    def breadth_search(self):
        """
        the breadth search function, consumes the current queue until exhausted.
        Its the responsibility of the caller to iterate and replenish the queue.
        """
        while self.queue:
            obj = self.queue.pop()
            saddle = obj[LOCAL_LINKER].saddle
            # This will fail if we encounter a runoff or some other oddball scenarios.
            ##############
            try:
                next_linker = obj[LOCAL_LINKER].linker_other_side_of_saddle()[0]
            except:
                # keep track of any low saddles that lead up to an edge.
                # We'll cull any invalid ones at the caller
                if saddle.edgeEffect:
                    if obj[LOWEST_SADDLE]:
                        self.candidate_offmap_saddles.add(obj[LOWEST_SADDLE])
                else:
                    print(f"BAD: {saddle}")
                continue
            #################
            summit_under_test = next_linker.summit

            if summit_under_test.edgeEffect:
                if obj[LOWEST_SADDLE]:
                    self.candidate_offmap_saddles.add(obj[LOWEST_SADDLE])

            viable_saddle = obj[LOWEST_SADDLE] if obj[LOWEST_SADDLE] else saddle
            # lowest seen already lower than the candidate? bail.
            if self.candidate_key_col and viable_saddle.elevation < self.candidate_key_col.elevation:
                continue

            if summit_under_test.elevation > self.summit.elevation:

                if not self.candidate_key_col:
                    self.candidate_key_col = viable_saddle
                    self.candidate_parent = summit_under_test
                    continue

                # If we have an existing candidate col and we're the higher one, use us.
                if self.candidate_key_col and self.candidate_key_col.elevation < viable_saddle.elevation:
                    self.candidate_key_col = viable_saddle
                    self.candidate_parent = summit_under_test
                    continue

                # If we have an existing candidate col and we're the same height, use the one with the taller summit
                elif self.candidate_key_col and self.candidate_key_col.elevation == viable_saddle.elevation:
                    if self.candidate_parent.elevation < summit_under_test.elevation:
                        self.candidate_key_col = viable_saddle
                        self.candidate_parent = summit_under_test
                        continue


            #
            # add logic for handling map edges here.
            #

            # check for low saddle.
            if not obj[LOWEST_SADDLE]:
                lowest = saddle
            elif obj[LOWEST_SADDLE] and saddle.elevation < obj[LOWEST_SADDLE].elevation:
                lowest = saddle
            else:
                lowest = obj[LOWEST_SADDLE]

            # Alright, we're done here, queue up the next summits and add them to the next ring.
            for next_saddle_linker in summit_under_test.saddles:
                if next_saddle_linker.id == next_linker.id or next_saddle_linker.disqualified:
                    continue
                self.queue.appendleft((next_saddle_linker, lowest))