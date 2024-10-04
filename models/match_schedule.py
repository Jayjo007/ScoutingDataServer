from extensions import db  # Adjust the import based on your project structure
from .matchdata import MatchData  # Assuming MatchData is in data_validation.py

class MatchSchedule(db.Model):
    __tablename__ = 'match_schedule'
    eventKey = db.Column(db.String(50), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(50), primary_key=True)
    red1 = db.Column(db.String(50))
    red2 = db.Column(db.String(50))
    red3 = db.Column(db.String(50))
    blue1 = db.Column(db.String(50))
    blue2 = db.Column(db.String(50))
    blue3 = db.Column(db.String(50))

    def __init__(self, eventKey, matchNumber, matchLevel, red1, red2, red3, blue1, blue2, blue3):
        self.eventKey = eventKey
        self.matchNumber = matchNumber
        self.matchLevel = matchLevel
        self.red1 = red1
        self.red2 = red2
        self.red3 = red3
        self.blue1 = blue1
        self.blue2 = blue2
        self.blue3 = blue3

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def checkIsScouted(self):
        return MatchData.query.filter_by(eventKey=self.eventKey, matchNumber=self.matchNumber, matchLevel=self.matchLevel).count() > 0

    def checkIfTeamScouted(self, team):
        return MatchData.query.filter_by(eventKey=self.eventKey, matchNumber=self.matchNumber, matchLevel=self.matchLevel, teamNumber=team).count() > 0

    def checkIfTeamHasPlayedMatch(self, team):
        return MatchData.query.filter_by(eventKey=self.eventKey, teamNumber=team).count() > 0

    def checkIfCanBePreviewed(self):
        return any(self.checkIfTeamHasPlayedMatch(team) for team in [self.red1, self.red2, self.red3, self.blue1, self.blue2, self.blue3])
    
    def renderEventLevel(self):
        levels = {'qm': "Qualification Match", 'f': "Finals Match"}
        return levels.get(self.matchLevel, "Playoff Match")
