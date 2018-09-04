# from sqlalchemy.sql import func
from datetime import datetime
from project import db


class Experiment(db.Model):
    __tablename__ = 'experiments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    # start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(128), nullable=False)
    result = db.Column(db.String(4096))
    test_data = db.Column(db.String(255))
    train_data = db.Column(db.String(255))

    def __init__(self, name, type, test_data=None, train_data=None, start_date=datetime.utcnow()):
        self.name = name
        self.type = type
        self.test_data = test_data
        self.train_data = train_data
        self.start_date = start_date

    def to_json(self):
        return {
                'id': self.id,
                'name': self.name,
                'type': self.type,
                'train_data': self.train_data,
                'test_data': self.test_data,
                'result': self.result,
                'start_date': self.start_date
            }