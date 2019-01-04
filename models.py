import datetime
from config import app, db

class FetchedUrl(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.Text, unique = True, nullable = False)
    data = db.Column(db.Text, nullable = False)
    added_at = db.Column(db.DateTime, default = datetime.datetime.now)

    def __repr__(self):
        return "URL {0} at {1}".format(self.url, self.added_at)

if __name__ == '__main__':
    db.create_all()
