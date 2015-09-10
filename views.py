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
import re
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

class Ideas(BaseHandler):
    def get(self):
        self.render('ideas')

class Experiences(BaseHandler):
    def get(self):
        context = {'Categories': Categories, 'Categories_map': Categories_map, 'articles': {}}
        for category in Categories:
            articles = Article.query(Article.category==category).order(-Article.date).fetch(limit=10)
            context['articles'][category] = []
            for article in articles:
                info = {
                    'title': article.title,
                    'date': article.date.strftime("%Y-%m-%d"),
                    'index': article.index,
                }
                context['articles'][category].append(info)

        self.render('experiences', context)

class PerExperience(BaseHandler):
    def get(self, category):
        page_size = 5
        articles, cursor, more = Article.query(Article.category==category).order(-Article.date).fetch_page(page_size, start_cursor=Cursor())
        context = {'Categories': Categories, 'Categories_map': Categories_map, 'cur_category': category, 'articles':[]}
        context['cursor'] = cursor.urlsafe() if more else ''
        for article in articles:
            info = {
                'title': article.title,
                'content': re.sub(r'<img.*?>', '', article.content),
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
            }
            res = re.search(r'<img.*?src="(.*?)".*?>', article.content)
            if res:
                info['image'] = res.group(1)
            context['articles'].append(info)
        self.render('per_experience', context)

    def post(self, category):
        self.response.headers['Content-Type'] = 'application/json'
        page_size = 5
        cursor = self.request.get('cursor')
        if not cursor:
            context = {'error': True, 'message': 'Invalid cursor'}
            return

        cursor = Cursor(urlsafe=cursor)
        articles, cursor, more = Article.query(Article.category==category).order(-Article.date).fetch_page(page_size, start_cursor=cursor)
        context = {'error': False, 'cur_category': category, 'articles':[]}
        context['cursor'] = cursor.urlsafe() if more else ''
        for article in articles:
            info = {
                'title': article.title,
                'content': re.sub(r'<img.*?>', '', article.content),
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
            }
            res = re.search(r'<img.*?src="(.*?)".*?>', article.content)
            if res:
                info['image'] = res.group(1)
            context['articles'].append(info)

        self.response.out.write(json.dumps(context))

class Record(BaseHandler):
    def get(self, category, record_index):
        context = {'Categories': Categories, 'Categories_map': Categories_map, 'cur_category': category}

        article = Article.query(Article.category==category, Article.index==int(record_index)).get()
        if not article:
            self.render('record', context)
            return

        info = {
            'title': article.title,
            'content': article.content,
            'date': article.date.strftime("%Y-%m-%d"),
            'index': article.index,
        }
        context['article'] = info

        next_article = Article.query(Article.category==article.category, Article.index==article.index + 1).get()
        if next_article:
            logging.info(str(next_article.key.id())+' '+str(next_article.index))
            info = {
                'title': next_article.title,
                'index': next_article.index,
            }
            context['next'] = info

        prev_article = Article.query(Article.category==article.category, Article.index==article.index - 1).get()
        if prev_article:
            info = {
                'title': prev_article.title,
                'index': prev_article.index,
            }
            context['previous'] = info

        # context['comments'] = []
        # comments = Comment.query(Comment.belonged==article.key).order(-Comment.date).fetch()
        # for i in range(0, len(comments)):
        #     comment = comments[i]
        #     info = {
        #         'name': comment.nickname,
        #         'date': comment.date.strftime("%Y-%m-%d %H:%M"),
        #         'content': comment.content,
        #     }
        #     context['comments'].append(info)
            
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

            if (not name) or (not email) or (not subject) or (not content):
                raise Exception('No fields can be empty.')

            message = mail.EmailMessage()
            message.sender = 'yuxuanalan@appspot.gserviceaccount.com'
            message.to = 'teststaybaka@gmail.com'
            message.subject = subject
            message.body = 'An email send from '+name+' ('+email+').\n\n'+ content
            message.send()

            self.notify('Thank you very much. I\'ve received your email :)', 'success')
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
