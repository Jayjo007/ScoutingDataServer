from extensions import db  # Adjust the import based on your project structure

class ActiveEventKey(db.Model):
    __tablename__ = 'activeeventkey'
    index = db.Column(db.Integer(), primary_key=True)
    activeEventKey = db.Column(db.String(50))

    def __init__(self, activeEventKey):
        self.index = 1
        self.activeEventKey = activeEventKey
