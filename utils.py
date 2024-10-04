from extensions import db
from models import ActiveEventKey

def getActiveEventKey():
    if (not ActiveEventKey.query.first() == None):
        return ActiveEventKey.query.first().activeEventKey
    return "Undefined"

def getCurrentMatchLevel():
    if (not ActiveEventKey.query.filter_by(index=2).first() == None):
        return ActiveEventKey.query.filter_by(index=2).first().activeEventKey
    return "qm"