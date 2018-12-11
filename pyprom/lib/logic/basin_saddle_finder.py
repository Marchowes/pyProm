import logging
from collections import deque
from ..containers.saddles import SaddlesContainer
from ..locations.runoff import Runoff

class CircuitFinder:
    def __init__(self, domain):
        self.domain = domain
        self.logger = logging.getLogger('{}'.format(__name__))
        self.disqualifiedSaddles = []
        self.tempDebug = {}


    def detect_tree_loops(self):
        deleted = 0 ##
        for idx, saddle in enumerate(self.domain.saddles):
            # if the saddle is disqualified, move on.
            if saddle.disqualified:
                continue
            self.loop_detection(saddle)
            self.logger.info("Deleted round {}: {}".format(len(self.disqualifiedSaddles)-deleted)) ##
            deleted = len(self.disqualifiedSaddles) ##
        self.logger.info("Disqualified: {} Loop Saddles".format(len(self.disqualifiedSaddles)))

    def loop_detection(self, saddle):
        exemptLinkers = {}
        lookback = {} # {saddleid: previous}
        queue = deque()
        queue.append(saddle)
        while queue:
            saddle_under_test = queue.popleft()
            # iterate through all non disqualified neighboring saddles.
            for next_saddle_hash in saddle_under_test.all_neighbors_with_summit(exemptLinkers=exemptLinkers):

                exemptLinkers[next_saddle_hash["linker"].id] = True
                next_saddle = next_saddle_hash['saddle']
                # next saddle already been looked at? thats a loop -- maybe
                loopRoot = lookback.get(next_saddle.id, None)
                # if next_saddle was already explored.
                if loopRoot:
                    #if not the previous saddle from SUT
                    #if loopRoot != lookback[saddle_under_test.id]:
                        # run basin saddle detection.
                    self.basin_saddle_detector(loopRoot, next_saddle, lookback)
                    # otherwise skip.
                    #else:
                        # self.logger.info("oh")
                        #continue
                else:
                    queue.append(next_saddle)
                lookback[next_saddle.id] = saddle_under_test

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
        # self.logger.info("Basin Saddle: {}".format(lowest))
        lowest.disqualify_self_and_linkers(tooLow=True) # TODO: make a basin saddle marker.
        self.disqualifiedSaddles.append(lowest)
        self.tempDebug[lowest.id] = {'loopRoot': loopRoot, 'loopLast':loopLast, 'loopPath': loopPath}




class CircuitFinder3:
    def __init__(self, saddles):
        """
        :param saddles: SaddlesContainer
        :raises: TypeError
        """
        if not isinstance(saddles, SaddlesContainer):
            raise TypeError("Saddles must be SaddlesContainer")
        self.saddles = saddles
        self.logger = logging.getLogger('{}'.format(__name__))
        self.disqualifiedSaddles = []
        self.tempDebug = {}

    def detect_tree_loops(self):
        deleted = 0 ##
        oldDQ = []
        for idx, saddle in enumerate(self.saddles):
            # if the saddle is disqualified, move on.
            if saddle.disqualified:
                continue
            self.loop_detection(saddle)
            delta = [x for x in self.disqualifiedSaddles if x not in oldDQ]
            self.logger.info("Deleted round {}: {}".format(idx, len(self.disqualifiedSaddles)-deleted)) ##
            if delta:
                for x in delta:
                    self.logger.info("Deleted: {}".format(x.__repr__()))
            oldDQ = self.disqualifiedSaddles[:]
            deleted = len(self.disqualifiedSaddles) ##
        self.logger.info("Disqualified: {} Loop Saddles".format(len(self.disqualifiedSaddles)))

    def loop_detection(self, saddle):
        exemptLinkers = {}
        lookback = {} # {saddleid: previousSaddle}
        queue = deque()
        queue.append(saddle)
        lookback[saddle.id] = None # Root Node
        while queue:
            saddle_under_test = queue.popleft()
            summits = set()
            # iterate through all non disqualified neighboring saddles.
            for localLinker in saddle_under_test.summits:
                summits.add(localLinker.summit)
                if exemptLinkers.get(localLinker.id):
                    continue


                exemptLinkers[localLinker.id] = True


                for remoteLinker in localLinker.linkers_to_saddles_connected_via_summit(excludeSelf=True, highToLow=True):
                    if exemptLinkers.get(remoteLinker.id):
                        continue
                    next_saddle = remoteLinker.saddle
                    exemptLinkers[remoteLinker.id] = True
                    # self referential? die!
                    #if next_saddle == saddle_under_test: # remoteLinker.saddle.id == saddle_under_test.id:
                    if next_saddle.id == saddle_under_test.id:
                        self.logger.info("Self Referential! {}, {}".format(saddle_under_test, saddle_under_test.id)) ####
                        saddle_under_test.disqualify_self_and_linkers(singleSummit=True)
                        self.disqualifiedSaddles.append(saddle_under_test)
                        continue

                    #next_saddle = remoteLinker.saddle
                    loopConnection = lookback.get(next_saddle.id, None)

                    if loopConnection:
                        # run basin saddle detection.
                        self.basin_saddle_detector(next_saddle, saddle_under_test, lookback)

                    else:
                        queue.append(next_saddle)
                    lookback[next_saddle.id] = saddle_under_test
            if len(summits) <= 1 and not isinstance(saddle_under_test, Runoff):
                self.logger.info("Dis Fucking Qualified! {}, {}".format(saddle_under_test, saddle_under_test.id))  ####
                saddle_under_test.disqualify_self_and_linkers(singleSummit=True)
                self.disqualifiedSaddles.append(saddle_under_test)

    def basin_saddle_detector(self, loopConnection, current_saddle, lookback):
        them = []
        us = [current_saddle]
        them = [loopConnection]
        usCurrentSaddle = current_saddle
        themCurrentSaddle = loopConnection
        while True:
            # grab the previously explored saddle ahead of currentSaddle
            usCurrentSaddle = lookback.get(usCurrentSaddle.id)
            if usCurrentSaddle:
                us.append(usCurrentSaddle)
            else:
                break

        while True:
            if themCurrentSaddle in us:
                break
            themCurrentSaddle = lookback.get(themCurrentSaddle.id)
            if themCurrentSaddle:
                them.append(themCurrentSaddle)
            else:
                self.logger.info("SOMETHING WRONG HAS HAPPENED.")
                break
        found = False
        for idx, saddle in enumerate(us):
            if saddle == themCurrentSaddle:
                usSlice = us[:idx]
                found = True
                break

        if not found:
            self.tempDebug[current_saddle.id] = {'ok': False, 'usSlice': usSlice, 'us': usCurrentSaddle,
                                         'them': themCurrentSaddle}
            return

        lowest = None
        AllSaddleCandidatesUnordered = usSlice + them
        for saddle in AllSaddleCandidatesUnordered:
            if not lowest or saddle.elevation < lowest.elevation:
                lowest = saddle
        lowest.disqualify_self_and_linkers(tooLow=True) # TODO: make a basin saddle marker.
        self.disqualifiedSaddles.append(lowest)
        self.tempDebug[lowest.id] = {'ok': True, 'usSlice': usSlice, 'us':usCurrentSaddle, 'them': themCurrentSaddle}











class CircuitFinder2:
    def __init__(self, saddles):
        """
        :param saddles: SaddlesContainer
        :raises: TypeError
        """
        if not isinstance(saddles, SaddlesContainer):
            raise TypeError("Saddles must be SaddlesContainer")
        self.saddles = saddles
        self.logger = logging.getLogger('{}'.format(__name__))
        self.disqualifiedSaddles = []
        self.tempDebug = {}

    def detect_tree_loops(self):

        for idx, saddle in enumerate(self.saddles):
            self.logger.info("IDX: {}, Appraising {}".format(idx, saddle))
            # if the saddle is disqualified, move on.
            if saddle.disqualified:
                continue
            self.loop_detection(saddle)

    def loop_detection(self, saddle):
        if len(saddle.summits_set) < 2:
            saddle.disqualify_self_and_linkers(singleSummit=True)
        if saddle.disqualified:
            return
        exemptLinkers = {}
        lookback = {}
        queue = deque()
        root = saddle
        originLeg = saddle.summits[0]
        terminalLeg = saddle.summits[1]
        exemptLinkers[originLeg.id] = True
        lookback[originLeg.summit] = root
        remoteSaddles = originLeg.saddles_connected_via_summit(exemptLinkers=exemptLinkers)
        for linker in originLeg.linkers_to_saddles_connected_via_summit():
            exemptLinkers[linker.id] = True
        queue.extend(remoteSaddles)
        lookback = {first:root for first in remoteSaddles}

        lookback[saddle] = None

        while queue:
            saddle_under_test = queue.popleft()
            # iterate through all non disqualified neighboring saddles.
            for localLinker in saddle_under_test.summits:
                isLoop = localLinker.id == terminalLeg.id
                if isLoop:
                    us = self.basin_saddle_detector(root, saddle_under_test, lookback)
                    # did we disqualify another saddle? Then recursively rescan the saddle_under_test.
                    if not us:
                        self.loop_detection(root)
                    return
                if exemptLinkers.get(localLinker.id):
                    continue
                exemptLinkers[localLinker.id] = True
                for remoteLinker in localLinker.linkers_to_saddles_connected_via_summit(excludeSelf=True):
                    next_saddle = remoteLinker.saddle
                    if exemptLinkers.get(remoteLinker.id):
                        continue

                    # next saddle is single summit. Disqualify and move on.
                    if len(next_saddle.summits_set) < 2:
                        next_saddle.disqualify_self_and_linkers(singleSummit=True)
                        continue
                    if isinstance(next_saddle, Runoff):
                        continue

                    isLoop = remoteLinker.id == terminalLeg.id
                    if not isLoop and exemptLinkers.get(remoteLinker.id):
                        continue
                    if isLoop:
                        us = self.basin_saddle_detector(root, saddle_under_test, lookback)
                        # did we disqualify another saddle? Then recursively rescan the saddle_under_test.
                        if not us:
                            self.loop_detection(root)
                        return
                    exemptLinkers[remoteLinker.id] = True
                    queue.append(next_saddle)
                    lookback[next_saddle] = saddle_under_test

    def basin_saddle_detector(self, root, connection, lookback):
        if not connection:
            root.disqualify_self_and_linkers(singleSummit=True)
            self.logger.info("DQed SS: {}".format(root))
            return True
        candidates = [connection]
        current_saddle = connection
        lowest = connection
        while True:
            current_saddle = lookback[current_saddle]
            if not current_saddle:
                if lowest == root:
                    lowest.disqualify_self_and_linkers(tooLow=True)
                    self.logger.info("DQed: {}".format(lowest))
                    return True
                # Disqualify them.
                lowest.disqualify_self_and_linkers(tooLow=True)
                self.logger.info("DQed: {}".format(lowest))
                return False
            candidates.append(current_saddle)
            if current_saddle.elevation < lowest.elevation:
                lowest = current_saddle


