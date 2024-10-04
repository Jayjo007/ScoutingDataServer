from app import db

class PitScoutRecord(db.Model):
    __tablename__ = 'pitdata'
    teamNumber = db.Column(db.String(50), primary_key=True)
    eventKey = db.Column(db.String(50), primary_key=True)
    programmingLanguage = db.Column(db.String(50))
    drivetrain = db.Column(db.String(50))
    driveteam = db.Column(db.Integer())
    def __init__(self, data):
        self.teamNumber = data["teamNumber"]
        self.eventKey = data["event"]
        self.programmingLanguage = data["programmingLanguage"]
        self.drivetrain = data["drivetrainType"]
        self.driveteam = data["driveteam"]

    def __str__(self):
        return self.teamNumber