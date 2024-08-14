from utils.database import db

class WikipediaPage(db.Model):
    __tablename__ = 'wikipediaPages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    event_code = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(200), nullable=False)

    def as_dict(self):
        return {
                'id': self.id, 
                'title': self.title, 
                'language': self.language, 
                'views': self.views, 
                'event_code': self.event_code,
                'url':self.url
                }
