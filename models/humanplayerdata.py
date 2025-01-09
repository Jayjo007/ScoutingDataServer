from extensions import db  # Adjust the import based on your project structure

class HumanPlayerData(db.Model):
    __tablename__ = "humanplayerdata"
    teamNumber = db.Column(db.String(50), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(50), primary_key=True)
    eventKey = db.Column(db.String(50), primary_key=True)
    shotsMissed = db.Column(db.Integer())
    shotsMade = db.Column(db.Integer())

    def __init__(self, teamNumber, matchNumber, eventKey, matchLevel):
        self.teamNumber = teamNumber
        self.matchNumber = matchNumber
        self.eventKey = eventKey
        self.matchLevel = matchLevel
