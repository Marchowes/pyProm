import logging
from collections import deque

class CircuitFinder:
    def __init__(self, domain):
        self.domain = domain
        self.logger = logging.getLogger('{}'.format(__name__))
        self.disqualifiedSaddles = []


    def detect_tree_loops(self):
        for idx, saddle in enumerate(self.domain.saddles):
            # if the saddle is disqualified, move on.
            if saddle.disqualified:
                continue
            #exempt = {} # list of saddles
            #path = list()
            # while self.branchChaser(saddle, saddle, 0, exempt, path, disqualifiedSaddles) == True:
            #    pass
            self.loop_detection(saddle)
            self.logger.info(idx)
        self.logger.info("Disqualified: {} Loop Saddles".format(len(self.disqualifiedSaddles)))

    def loop_detection(self, saddle):
        master = saddle
        lookback = {} # {saddleid: previous}
        queue = deque()
        queue.append(saddle)
        while queue:
            saddle_under_test = queue.popleft()
            # iterate through all non disqualified neighboring saddles.
            for next_saddle in saddle_under_test.neighbors:
                # next saddle already been looked at? thats a loop -- maybe
                loopRoot = lookback.get(next_saddle.id, None)
                # if next_saddle was already explored.
                if loopRoot:
                    #if not the previous saddle from SUT
                    if loopRoot != lookback[saddle_under_test.id]:
                        # run basin saddle detection.
                        self.basin_saddle_detector(loopRoot, next_saddle, lookback)
                    # otherwise skip.
                    else:
                        continue
                else:
                    lookback[next_saddle.id] = saddle_under_test
                    queue.append(next_saddle)

    def basin_saddle_detector(self, loopRoot, loopLast, lookback):
        loopPath = list()
        currentSaddle = loopLast
        loopPath.append(currentSaddle)
        while True:
            # grab the previously explored saddle ahead of currentSaddle
            currentSaddle = lookback[currentSaddle.id]
            loopPath.append(currentSaddle)
            if currentSaddle == loopRoot:
                #circuit complete!
                break

        # this should be a list so if we have equal lowest we can mark one
        # as a basin candidate.
        lowest = None
        for saddle in loopPath:
            if not lowest or saddle.elevation < lowest.elevation:
                lowest = saddle
        self.logger.info("Basin Saddle: {}".format(lowest))
        lowest.disqualify_self_and_linkers(tooLow=True) # TODO: make a basin saddle marker.
        self.disqualifiedSaddles.append(lowest)




