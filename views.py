import cgi
import urllib
import os
import logging
import jinja2
import webapp2
import json
import cStringIO
import itertools
import mimetools
import mimetypes
import urllib
import urllib2
from webapp2_extras import sessions
from jinja2 import Undefined
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.ext.webapp import blobstore_handlers

from models import *

class SilentUndefined(Undefined):
    '''
    Dont break pageloads because vars arent there!
    '''
    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.exception('JINJA2: something was undefined!')
        return None

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=False,
    undefined=SilentUndefined)
env.globals = {
    'uri_for': webapp2.uri_for,
}

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()

    def render(self, tempname, context = {}):
        path = 'template/' + tempname + '.html'
        template = env.get_template(path)
        self.response.write(template.render(context))

    def notify(self, message, message_type='error'):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'type': message_type,
            'message': message
        }))

class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)

class Home(BaseHandler):
    def get(self):
        self.render('home')

class About(BaseHandler):
    def get(self):
        self.render('about')

class Projects(BaseHandler):
    def get(self):
        self.render('projects')

class DanTube(BaseHandler):
    def get(self):
        self.render('dantube')
        
class ActionGame(BaseHandler):
    def get(self):
        self.render('action_game')

class Experiences(BaseHandler):
    def get(self):
        context = {}
        for i in range(0, len(Categories)):
            category = Categories[i]
            articles = Article.query(Article.category==category).order(-Article.date).fetch(limit=10)
            context[category] = []
            for j in range(0, len(articles)):
                article = articles[j]
                info = {
                    'title': article.title,
                    'date': article.date.strftime("%Y-%m-%d"),
                    'id': article.key.id(),
                }
                context[category].append(info)

        self.render('experiences', context)

class PerExperience(BaseHandler):
    def get(self, category):
        page_size = 10
        try:
            page = int(self.request.get('page'))
        except Exception, e:
            page = 1

        articles = Article.query(Article.category==category).order(-Article.date).fetch(offset=(page-1)*page_size, limit=page_size)
        context = {category:'active', 'articles':[]}
        for article in articles:
            info = {
                'title': article.title,
                'content': article.content,
                'date': article.date.strftime("%Y-%m-%d"),
                'id': article.key.id(),
            }
            if len(article.images) > 0:
                info['image'] = images.get_serving_url(article.images[0])
            context['articles'].append(info)
        self.render('per_experience', context)

class Record(BaseHandler):
    def get(self, record_id):
        article = Article.get_by_id(int(record_id))
        context = {article.category: 'active'}
        info = {
            'title': article.title,
            'content': article.content,
            'date': article.date.strftime("%Y-%m-%d"),
            'category': article.category,
            'id': article.key.id(),
        }
        context['article'] = info

        articles = Article.query(Article.category==article.category).order(-Article.date).fetch()
        idx = articles.index(article)
        if idx > 0:
            temp = articles[idx-1]
            info = {
                'title': temp.title,
                'id': temp.key.id()
            }
            context['next'] = info
        if idx < len(articles) - 1:
            temp = articles[idx+1]
            info = {
                'title': temp.title,
                'id': temp.key.id()
            }
            context['previous'] = info

        context['comments'] = []
        comments = Comment.query(Comment.belonged==article.key).order(-Comment.date).fetch()
        for i in range(0, len(comments)):
            comment = comments[i]
            info = {
                'name': comment.nickname,
                'date': comment.date.strftime("%Y-%m-%d %H:%M"),
                'content': comment.content,
            }
            context['comments'].append(info)
            
        self.render('record', context)

class Contact(BaseHandler):
    def get(self):
        self.render('contact')

class HireMe(BaseHandler):
    def get(self):
        self.render('hire_me')

class SendEmail(BaseHandler):
    def post(self):
        try:
            name = self.request.get('name').strip()
            email = self.request.get('email').strip()
            subject = self.request.get('subject').strip()
            content = self.request.get('content').strip()

            message = mail.EmailMessage()
            message.sender = 'yuxuanalan@appspot.gserviceaccount.com'
            message.to = 'teststaybaka@gmail.com'
            message.subject = subject
            message.body = 'An email send from '+email+'.\n\n'+ content
            message.send()

            self.notify('Thank you. I\'ve recieved your email :)', 'success')
        except Exception, e:
            self.notify(str(e), 'error')

class CommentPost(BaseHandler):
    def post(self, record_id):
        try:
            article = Article.get_by_id(int(record_id))
            name = self.request.get('name').strip()
            email = self.request.get('email').strip()
            content = self.request.get('content').strip()

            message = mail.EmailMessage()
            message.sender = 'yuxuanalan@appspot.gserviceaccount.com'
            message.to = 'teststaybaka@gmail.com'
            message.subject = name+' posted a comment on "'+article.title+'"'
            message.body = content
            message.send()

            comment = Comment(belonged = article.key, email = email, nickname = name, content = content)
            comment.put()

            self.notify('Thank you for your comment :)', 'success')
        except Exception, e:
            self.notify(str(e), 'error')
