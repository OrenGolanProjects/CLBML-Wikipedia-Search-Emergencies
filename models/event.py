from utils.database import db

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    language = db.Column(db.String(80), nullable=False)
    created_datetime = db.Column(db.String(80), nullable=False)
    event_code = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {
                'id': self.id, 
                'name': self.name, 
                'language': self.language, 
                'created_datetime': self.created_datetime,
                'event_code': self.event_code
                }
