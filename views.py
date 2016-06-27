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
    def render(self, tempname, context = {}):
        context.update({
            'Categories': Categories,
            'Categories_map': Categories_map,
        })
        path = 'template/' + tempname + '.html'
        template = env.get_template(path)
        self.response.write(template.render(context))

    def response_json(self, context = {}):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(context))

    def notify(self, message, message_type='error'):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'type': message_type,
            'message': message
        }))

class Home(BaseHandler):
    def get(self):
        context = {'articles': []}
        articles, cursor, more = Article.query().order(-Article.date).fetch_page(PAGE_SIZE, start_cursor=Cursor())
        context['cursor'] = cursor.urlsafe() if more else ''
        for article in articles:
            info = {
                'title': article.title,
                'content': re.sub(r'<img.*?>', '', article.content),
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
                'category': article.category,
            }
            res = re.search(r'<img.*?src="(.*?)".*?>', article.content)
            if res:
                info['image'] = res.group(1)
            context['articles'].append(info)
        self.render('articles', context)

    def post(self):
        cursor = self.request.get('cursor')
        if not cursor:
            context = {'error': True, 'message': 'Invalid cursor'}
            self.response_json(context)
            return

        cursor = Cursor(urlsafe=cursor)
        articles, cursor, more = Article.query().order(-Article.date).fetch_page(PAGE_SIZE, start_cursor=cursor)
        context = {'error': False, 'articles':[]}
        context['cursor'] = cursor.urlsafe() if more else ''
        for article in articles:
            info = {
                'title': article.title,
                'content': re.sub(r'<img.*?>', '', article.content),
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
                'category': article.category,
            }
            res = re.search(r'<img.*?src="(.*?)".*?>', article.content)
            if res:
                info['image'] = res.group(1)
            context['articles'].append(info)
        self.response_json(context)

class Articles(BaseHandler):
    def get(self, category):
        if category not in Categories:
            self.redirect(self.uri_for('home'))
            return

        context = {'articles': []}
        articles, cursor, more = Article.query(Article.category==category).order(-Article.date).fetch_page(PAGE_SIZE, start_cursor=Cursor())
        context['cursor'] = cursor.urlsafe() if more else ''
        for article in articles:
            info = {
                'title': article.title,
                'content': re.sub(r'<img.*?>', '', article.content),
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
                'category': article.category,
            }
            res = re.search(r'<img.*?src="(.*?)".*?>', article.content)
            if res:
                info['image'] = res.group(1)
            context['articles'].append(info)
        self.render('articles', context)

    def post(self, category):
        if category not in Categories:
            self.notify('Invalid category', 'error')
            return

        cursor = self.request.get('cursor')
        if not cursor:
            context = {'error': True, 'message': 'Invalid cursor'}
            self.response_json(context)
            return

        cursor = Cursor(urlsafe=cursor)
        articles, cursor, more = Article.query(Article.category==category).order(-Article.date).fetch_page(PAGE_SIZE, start_cursor=cursor)
        context = {'error': False, 'articles':[]}
        context['cursor'] = cursor.urlsafe() if more else ''
        for article in articles:
            info = {
                'title': article.title,
                'content': re.sub(r'<img.*?>', '', article.content),
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
                'category': article.category,
            }
            res = re.search(r'<img.*?src="(.*?)".*?>', article.content)
            if res:
                info['image'] = res.group(1)
            context['articles'].append(info)
        self.response_json(context)

class PerArticle(BaseHandler):
    def get(self, category, index):
        if category not in Categories:
            self.redirect(self.uri_for('home'))
            return

        article = Article.query(Article.category==category, Article.index==int(index)).get()
        if not article:
            self.redirect(self.uri_for('home'))
            return

        context = {
            'article': {
                'title': article.title,
                'content': article.content,
                'date': article.date.strftime("%Y-%m-%d"),
                'index': article.index,
                'category': article.category,
            }
        }

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

        self.render('article', context)

class About(BaseHandler):
    def get(self):
        self.render('about')

class Contact(BaseHandler):
    def get(self):
        self.render('contact')

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

            context = {
                'message': 'Thank you very much. I\'ve received your message. :)',
                'error': False,
            }
            self.render('sent', context)
        except Exception, e:
            context = {
                'message': str(e),
                'error': True,
            }
            self.render('sent', context)
