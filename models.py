from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images
from google.appengine.datastore.datastore_query import Cursor
import time
import datetime
import re

def time_to_seconds(time):
  return int((time - datetime(2000, 1, 1)).total_seconds())

Categories = ['dantube', 'ybd', 'notes']
Categories_map = {'dantube': 'DanTube', 'ybd': 'YBD', 'notes': 'Notes'}
PAGE_SIZE = 5

class Article(ndb.Model):
    index = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty(indexed=False)
    content = ndb.TextProperty(indexed=False)
    # images = ndb.BlobKeyProperty(repeated=True)
    category = ndb.StringProperty(choices=Categories)
    date = ndb.DateTimeProperty()

    def preview_info(self):
        info = {
            'title': self.title,
            'date': self.date.strftime("%Y-%m-%d"),
            'index': self.index,
            'category': self.category,
        }
        
        content = re.sub(r'<img.*?>', '', self.content)
        content = re.sub(r'<a.*?>.*?</a>', '', content)
        info['content'] = content

        res = re.search(r'<img.*?src="(.*?)".*?>', self.content)
        if res:
            info['image'] = res.group(1)

        return info

class Comment(ndb.Model):
    belonged = ndb.KeyProperty()
    email = ndb.StringProperty(indexed=False)
    nickname = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    content = ndb.TextProperty()
