from google.appengine.ext import db
class Rank(db.Model):
    name = db.StringProperty()
    uniqueid = db.StringProperty()
    rank = db.IntegerProperty()
    category = db.StringProperty()
