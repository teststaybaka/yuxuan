from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.datastore.datastore_query import Cursor
import time
import datetime

def time_to_seconds(time):
  return int((time - datetime(2000, 1, 1)).total_seconds())

Categories = ['dantube', 'ybd', 'course', 'others']
Categories_map = {'dantube': 'DanTube', 'ybd': 'YBD', 'course': 'Scholar', 'others': 'Notes'}
PAGE_SIZE = 2

class Article(ndb.Model):
    index = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty(indexed=False)
    # images = ndb.BlobKeyProperty(repeated=True)
    category = ndb.StringProperty(choices=Categories)
    date = ndb.DateTimeProperty()

class Comment(ndb.Model):
    belonged = ndb.KeyProperty()
    email = ndb.StringProperty(indexed=False)
    nickname = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    content = ndb.TextProperty()
