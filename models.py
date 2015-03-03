from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images

class Article(ndb.Model):
    content = ndb.TextProperty()
    images = ndb.BlobKeyProperty(repeated=True)
    category = ndb.StringProperty()
