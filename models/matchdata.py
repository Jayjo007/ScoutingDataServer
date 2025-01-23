from extensions import db
from utils import getCurrentMatchLevel
from datetime import datetime

class MatchData(db.Model):
    __tablename__ = 'match_data'
    teamNumber = db.Column(db.String(10), primary_key=True)
    eventKey = db.Column(db.String(15), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(50), primary_key=True)
    #insert gamespecific
    al4ca = db.Column(db.Integer()) # acronym: Autonomous Level 4 Coral (Hexant) A
    al4cb = db.Column(db.Integer(), default=0)
    al4cc = db.Column(db.Integer(), default=0)
    al4cd = db.Column(db.Integer(), default=0)
    al4ce = db.Column(db.Integer(), default=0)
    al4cf = db.Column(db.Integer(), default=0)
    al3ca = db.Column(db.Integer(), default=0)
    al3cb = db.Column(db.Integer(), default=0)
    al3cc = db.Column(db.Integer(), default=0)
    al3cd = db.Column(db.Integer(), default=0)
    al3ce = db.Column(db.Integer(), default=0)
    al3cf = db.Column(db.Integer(), default=0)
    al2ca = db.Column(db.Integer(), default=0)
    al2cb = db.Column(db.Integer(), default=0)
    al2cc = db.Column(db.Integer(), default=0)
    al2cd = db.Column(db.Integer(), default=0)
    al2ce = db.Column(db.Integer(), default=0)
    al2cf = db.Column(db.Integer(), default=0)
    al1ca = db.Column(db.Integer(), default=0)
    al1cb = db.Column(db.Integer(), default=0)
    al1cc = db.Column(db.Integer(), default=0)
    al1cd = db.Column(db.Integer(), default=0)
    al1ce = db.Column(db.Integer(), default=0)
    al1cf = db.Column(db.Integer(), default=0)
    tl4ca = db.Column(db.Integer(), default=0) #Teleop
    tl4cb = db.Column(db.Integer(), default=0) 
    tl4cc = db.Column(db.Integer(), default=0)
    tl4cd = db.Column(db.Integer(), default=0)
    tl4ce = db.Column(db.Integer(), default=0)
    tl4cf = db.Column(db.Integer(), default=0)
    tl3ca = db.Column(db.Integer(), default=0)
    tl3cb = db.Column(db.Integer(), default=0)
    tl3cc = db.Column(db.Integer(), default=0)
    tl3cd = db.Column(db.Integer(), default=0)
    tl3ce = db.Column(db.Integer(), default=0)
    tl3cf = db.Column(db.Integer(), default=0)
    tl2ca = db.Column(db.Integer(), default=0)
    tl2cb = db.Column(db.Integer(), default=0)
    tl2cc = db.Column(db.Integer(), default=0)
    tl2cd = db.Column(db.Integer(), default=0)
    tl2ce = db.Column(db.Integer(), default=0)
    tl2cf = db.Column(db.Integer(), default=0)
    tl1ca = db.Column(db.Integer(), default=0)
    tl1cb = db.Column(db.Integer(), default=0)
    tl1cc = db.Column(db.Integer(), default=0)
    tl1cd = db.Column(db.Integer(), default=0)
    tl1ce = db.Column(db.Integer(), default=0)
    tl1cf = db.Column(db.Integer(), default=0)
    al3aa = db.Column(db.Integer(), default=0) #Autonomous Level 3 Algae (Removal) (Triant) A
    al3ab = db.Column(db.Integer(), default=0)
    al3ac = db.Column(db.Integer(), default=0)
    al2aa = db.Column(db.Integer(), default=0)
    al2ab = db.Column(db.Integer(), default=0)
    al2ac = db.Column(db.Integer(), default=0)
    tl3aa = db.Column(db.Integer(), default=0) #Teleop
    tl3ab = db.Column(db.Integer(), default=0)
    tl3ac = db.Column(db.Integer(), default=0)
    tl2aa = db.Column(db.Integer(), default=0)
    tl2ab = db.Column(db.Integer(), default=0)
    tl2ac = db.Column(db.Integer(), default=0)
    aN = db.Column(db.Integer(), default=0) #auto net
    tN = db.Column(db.Integer(), default=0) #teleop net
    aP = db.Column(db.Integer(), default=0) #auto processor
    tP = db.Column(db.Integer(), default=0) #teleop processor
    endgameShallow = db.Column(db.Integer(), default=0)
    endgameDeep = db.Column(db.Integer(), default=0)
    tablet = db.Column(db.String(3))
    scouter = db.Column(db.String(50))
    timestamp = db.Column(db.String(50))

    def __init__(self, data):
        self.teamNumber = data["teamNumber"]
        self.eventKey = data["event"]
        self.matchNumber = data["matchNumber"]
        self.matchLevel = getCurrentMatchLevel()
        #insert gamespecific TODO
        self.al4ca = int(data["autoL4Coral"][0])
        self.al4cb = int(data["autoL4Coral"][1])
        self.al4cc = int(data["autoL4Coral"][2])
        self.al4cd = int(data["autoL4Coral"][3])
        self.al4ce = int(data["autoL4Coral"][4])
        self.al4cf = int(data["autoL4Coral"][5])
        self.al3ca = int(data["autoL3Coral"][0])
        self.al3cb = int(data["autoL3Coral"][1])
        self.al3cc = int(data["autoL3Coral"][2])
        self.al3cd = int(data["autoL3Coral"][3])
        self.al3ce = int(data["autoL3Coral"][4])
        self.al3cf = int(data["autoL3Coral"][5])
        self.al2ca = int(data["autoL2Coral"][0])
        self.al2cb = int(data["autoL2Coral"][1])
        self.al2cc = int(data["autoL2Coral"][2])
        self.al2cd = int(data["autoL2Coral"][3])
        self.al2ce = int(data["autoL2Coral"][4])
        self.al2cf = int(data["autoL2Coral"][5])
        self.al1ca = int(data["autoL1Coral"][0])
        self.al1cb = int(data["autoL1Coral"][1])
        self.al1cc = int(data["autoL1Coral"][2])
        self.al1cd = int(data["autoL1Coral"][3])
        self.al1ce = int(data["autoL1Coral"][4])
        self.al1cf = int(data["autoL1Coral"][5])
        self.tl4ca = int(data["teleL4Coral"][0])
        self.tl4cb = int(data["teleL4Coral"][1])
        self.tl4cc = int(data["teleL4Coral"][2])
        self.tl4cd = int(data["teleL4Coral"][3])
        self.tl4ce = int(data["teleL4Coral"][4])
        self.tl4cf = int(data["teleL4Coral"][5])
        self.tl3ca = int(data["teleL3Coral"][0])
        self.tl3cb = int(data["teleL3Coral"][1])
        self.tl3cc = int(data["teleL3Coral"][2])
        self.tl3cd = int(data["teleL3Coral"][3])
        self.tl3ce = int(data["teleL3Coral"][4])
        self.tl3cf = int(data["teleL3Coral"][5])
        self.tl2ca = int(data["teleL2Coral"][0])
        self.tl2cb = int(data["teleL2Coral"][1])
        self.tl2cc = int(data["teleL2Coral"][2])
        self.tl2cd = int(data["teleL2Coral"][3])
        self.tl2ce = int(data["teleL2Coral"][4])
        self.tl2cf = int(data["teleL2Coral"][5])
        self.tl1ca = int(data["teleL1Coral"][0])
        self.tl1cb = int(data["teleL1Coral"][1])
        self.tl1cc = int(data["teleL1Coral"][2])
        self.tl1cd = int(data["teleL1Coral"][3])
        self.tl1ce = int(data["teleL1Coral"][4])
        self.tl1cf = int(data["teleL1Coral"][5])
        self.al3aa = int(data["autoL3Algae"][0])
        self.al3ab = int(data["autoL3Algae"][1])
        self.al3ac = int(data["autoL3Algae"][2])
        self.al2aa = int(data["autoL2Algae"][0])
        self.al2ab = int(data["autoL2Algae"][1])
        self.al2ac = int(data["autoL2Algae"][2])
        self.tl3aa = int(data["teleL3Algae"][0])
        self.tl3ab = int(data["teleL3Algae"][1])
        self.tl3ac = int(data["teleL3Algae"][2])
        self.tl2aa = int(data["teleL2Algae"][0])
        self.tl2ab = int(data["teleL2Algae"][1])
        self.tl2ac = int(data["teleL2Algae"][2])
        self.aN = int(data["autoNet"])
        self.aP = int(data["autoProcessor"])
        self.tN = int(data["teleNet"])
        self.tP = int(data["teleProcessor"])
        if data["endgame"] == 1:
            self.endgameShallow = 1
        else:
            self.endgameShallow = 0
        if data["endgame"] == 2:
            self.endgameDeep = 1
        else: 
            self.endgameDeep = 0
        self.tablet = data["tablet"]
        self.scouter = data["scouter"]
        self.timestamp = datetime.now()

    def __str__(self):
        return self.teamNumber
    
    def renderEventLevel(self):
        if (self.matchLevel=='qm'):
            return "Qualification Match"
        elif (self.matchLevel=='f'):
            return "Finals Match"
        elif (self.matchLevel=="sf"):
            return "Playoff Match"
        else:
            return "Custom Match"
        
    def getCoralScored(self, level:int, auto:bool) -> int:
        if auto:
            if level==4:
                return self.al4ca+self.al4cb+self.al4cc+self.al4cd+self.al4ce+self.al4cf
            elif level==3:
                return self.al3ca+self.al3cb+self.al3cc+self.al3cd+self.al3ce+self.al3cf
            elif level==2:
                return self.al2ca+self.al2cb+self.al2cc+self.al2cd+self.al2ce+self.al2cf
            elif level==1:
                return self.al1ca+self.al1cb+self.al1cc+self.al1cd+self.al1ce+self.al1cf
        else:
            if level==4:
                return self.tl4ca+self.tl4cb+self.tl4cc+self.tl4cd+self.tl4ce+self.tl4cf
            elif level==3:
                return self.tl3ca+self.tl3cb+self.tl3cc+self.tl3cd+self.tl3ce+self.tl3cf
            elif level==2:
                return self.tl2ca+self.tl2cb+self.tl2cc+self.tl2cd+self.tl2ce+self.tl2cf
            elif level==1:
                return self.tl1ca+self.tl1cb+self.tl1cc+self.tl1cd+self.tl1ce+self.tl1cf
        return 0
    
    def getAlgaeRemoved(self, level:int, auto:bool) -> int:
        if auto:
            if level==3:
                return self.al3aa+self.al3ab+self.al3ac
            elif level==2:
                return self.al2aa+self.al2ab+self.al2ac
        else:
            if level==3:
                return self.tl3aa+self.tl3ab+self.tl3ac
            elif level==2:
                return self.tl2aa+self.tl2ab+self.tl2ac
        return 0
