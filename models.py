from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
import time
import datetime

def time_to_seconds(time):
  return int((time - datetime(2000, 1, 1)).total_seconds())

Categories = ['dantube', 'youmu_blade_dance', 'course', 'others']

class Article(ndb.Model):
    title = ndb.StringProperty()
    content = ndb.TextProperty()
    # images = ndb.BlobKeyProperty(repeated=True)
    category = ndb.StringProperty(choices=Categories)
    date = ndb.DateTimeProperty()

class Comment(ndb.Model):
    belonged = ndb.KeyProperty()
    email = ndb.StringProperty(indexed=False)
    nickname = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    content = ndb.TextProperty()
