class MatchAverages():
    def __init__(self, teamNumber):
        self.teamNumber = teamNumber
        #insert gamespecific
        self.defense = "N/A"
        

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
        """
        score += self.auto_speaker * 5
        score += self.auto_amp * 2
        score += self.tele_speaker * 2
        score += self.auto_amp
        score += self.trap * 5
        score += self.climb * 3
        score += self.auto_leave * 2
        """
        return score
