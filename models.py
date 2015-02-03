from google.appengine.ext import db
from google.appengine.ext import blobstore

class Article(db.Model):
    article_id = db.IntegerProperty()
    title = db.StringProperty()
    content = db.TextProperty()
    created_date = db.DateTimeProperty()
    edited_data = db.DateTimeProperty()
    category = db.StringProperty(choices=['project', 'idea'])

class Image(db.Model):
    img = db.BlobProperty();
    lines = db.IntegerProperty()

class Article_ID_Factory(db.Model):
    id_counter = db.IntegerProperty(required=True)

    def get_id(self):
        self.id_counter += 1
        self.put()
        return self.id_counter