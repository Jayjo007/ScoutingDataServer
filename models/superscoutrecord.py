from extensions import db

class SuperScoutRecord(db.Model):
    __tablename__ = 'superscoutdata'
    teamNumber = db.Column(db.String(50), primary_key=True)
    eventKey = db.Column(db.String(50), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(5))
    #startPosition = db.Column(db.String(10))
    #insert game specific
    broken = db.Column(db.Integer())
    notes = db.Column(db.String(255))
    overall = db.Column(db.String(10))
    def __init__(self, teamNumber, eventKey, matchNumber): 
        self.teamNumber = teamNumber
        self.eventKey = eventKey
        self.matchNumber = matchNumber

    def __str__(self):
        return self.teamNumber