class MatchAverages():
    def __init__(self, teamNumber):
        self.teamNumber = teamNumber
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
        """
        self.auto_speaker = (self.auto_speaker * self.count + matchData.auto_speaker) / (self.count + 1)
        self.auto_amp = (self.auto_amp * self.count + matchData.auto_amp) / (self.count + 1)
        self.tele_speaker = (self.tele_speaker * self.count + matchData.tele_speaker) / (self.count + 1)
        self.tele_amp = (self.tele_amp * self.count + matchData.tele_amp) / (self.count + 1)
        self.missed_tele_speaker = (self.missed_tele_speaker * self.count + matchData.missed_tele_speaker) / (self.count + 1)
        self.trap = (self.trap * self.count + matchData.trap) / (self.count + 1)
        
        if matchData.climb > 0:
            self.climb = (self.climb * self.climbAttempts + 1) / (self.climbAttempts + 1)
            self.climbAttempts += 1
        elif matchData.climb == -1:
            self.climb = (self.climb * self.climbAttempts) / (self.climbAttempts + 1)
            self.climbAttempts += 1
        
        if matchData.auto_leave != 0:
            self.auto_leave = (self.auto_leave * self.count + 1) / (self.count + 1)
        else:
            self.auto_leave = (self.auto_leave * self.count) / (self.count + 1)

        self.passing = (self.passing * self.count + matchData.passing) / (self.count + 1)
        self.count += 1
        """
        pass

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
