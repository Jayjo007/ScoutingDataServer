from app import db  # Adjust the import based on your project structure

class DataValidation(db.Model):
    __tablename__ = 'data_validation'
    eventKey = db.Column(db.String(15), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(50), primary_key=True)
    alliance = db.Column(db.Integer(), primary_key=True)
    #insert gamespecific data
