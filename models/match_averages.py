class MatchAverages():
    def __init__(self, teamNumber):
        self.teamNumber = teamNumber
        self.count = 0
        #insert gamespecific
        self.aL4C = 0
        self.aL3C = 0
        self.aL2C = 0
        self.aL1C = 0
        self.tL4C = 0
        self.tL3C = 0
        self.tL2C = 0
        self.tL1C = 0
        self.aL3A = 0
        self.aL2A = 0
        self.tL3A = 0
        self.tL2A = 0
        self.aNet = 0
        self.tNet = 0
        self.aProc = 0
        self.tProc = 0
        self.endgameShallow = 0
        self.endgameDeep = 0
        

    def addAverage(self, matchData):
        self.aL4C = (self.aL4C * self.count + matchData.getCoralScored(4, True)) / (self.count + 1)
        self.aL3C = (self.aL3C * self.count + matchData.getCoralScored(3, True)) / (self.count + 1)
        self.aL2C = (self.aL2C * self.count + matchData.getCoralScored(2, True)) / (self.count + 1)
        self.aL1C = (self.aL1C * self.count + matchData.getCoralScored(1, True)) / (self.count + 1)
        self.tL4C = (self.tL4C * self.count + matchData.getCoralScored(4, False)) / (self.count + 1)
        self.tL3C = (self.tL3C * self.count + matchData.getCoralScored(3, False)) / (self.count + 1)
        self.tL2C = (self.tL2C * self.count + matchData.getCoralScored(2, False)) / (self.count + 1)
        self.tL1C = (self.tL1C * self.count + matchData.getCoralScored(1, False)) / (self.count + 1)
        self.aL3A = (self.aL3A * self.count + matchData.getAlgaeRemoved(3, True)) / (self.count + 1)
        self.aL2A = (self.aL2A * self.count + matchData.getAlgaeRemoved(2, True)) / (self.count + 1)
        self.tL3A = (self.tL3A * self.count + matchData.getAlgaeRemoved(3, False)) / (self.count + 1)
        self.tL2A = (self.tL2A * self.count + matchData.getAlgaeRemoved(2, False)) / (self.count + 1)
        self.aNet = (self.aNet * self.count + matchData.aN) / (self.count + 1)
        self.tNet = (self.tNet * self.count + matchData.tN) / (self.count + 1)
        self.aProc = (self.aProc * self.count + matchData.aP) / (self.count + 1)
        self.tProc = (self.tProc * self.count + matchData.tP) / (self.count + 1)
        self.endgameShallow = (self.endgameShallow * self.count + matchData.endgameShallow) / (self.count + 1)
        self.endgameDeep = (self.endgameDeep * self.count + matchData.endgameDeep) / (self.count + 1)
        self.count += 1

    def scoreMatch(self):
        score = 0
        score += self.aL1C * 3
        score += self.aL2C * 4
        score += self.aL3C * 6
        score += self.aL4C * 7
        score += self.tL1C * 2
        score += self.tL2C * 3
        score += self.tL3C * 4
        score += self.tL4C * 5
        score += self.aNet * 4
        score += self.aProc * 6
        score += self.tProc * 6
        score += self.tNet * 4
        score += self.endgameShallow * 6
        score += self.endgameDeep * 12
        return score
