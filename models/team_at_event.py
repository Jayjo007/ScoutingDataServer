from extensions import db  # Adjust the import based on your project structure

class TeamAtEvent(db.Model):
    __tablename__ = 'teamatevent'
    eventKey = db.Column(db.String(50), primary_key=True)
    teamNumber = db.Column(db.Integer(), primary_key=True)

    def __init__(self, teamNumber, eventKey):
        self.teamNumber = teamNumber
        self.eventKey = eventKey
