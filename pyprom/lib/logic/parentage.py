"""
pyProm: Copyright 2020.

This software is distributed under a license that is described in
the LICENSE file that accompanies it.

This library contains a class for manipulating a pyProm Prominence Island
"""


# Use static values as they are a bit more performant and we'll be using them a lot.
LOCAL_LINKER = 0
LOWEST_SADDLE = 1
HIGHEST_SUMMIT = 2

class ProminenceIslandFinder:

    def __init__(self, summit):
        self.summit = summit
        self.highest_low_saddle = None
        self.current_queue = []
        self.next_queue = []
        self.candidate_key_col = None
        self.candidate_parent = None

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
            self.current_queue.append(obj)
        self.breadth_search()
        while self.next_queue:
            self.current_queue = self.next_queue
            self.next_queue = []
            self.breadth_search()

        return self.candidate_key_col, self.candidate_parent

    def breadth_search(self):
        """
        the breadth search function, consumes the current queue until exhausted.
        Its the responsibility of the caller to iterate and replenish the queue.
        """
        while self.current_queue:
            obj = self.current_queue.pop()
            saddle = obj[LOCAL_LINKER].saddle
            # This will fail if we encounter a runoff or some other oddball scenarios.
            ##############
            try:
                next_linker = obj[LOCAL_LINKER].linkers_to_summits_connected_via_saddle()[0]
            except:
                #print(f" BAD: {saddle}")
                continue
            #################
            summit_under_test = next_linker.summit

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
                if next_saddle_linker == next_linker or next_saddle_linker.disqualified:
                    continue
                self.next_queue.append((next_saddle_linker, lowest, highest))


####
"""
Troublesome scenarios: Equal height, 
Should we track equal heights along a path and use the low point between them as the col?

Edge, we need to track edges.
"""

