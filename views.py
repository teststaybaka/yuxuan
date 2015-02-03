import cgi
import urllib
import os
import logging
import jinja2
import webapp2
from webapp2_extras import sessions
from jinja2 import Undefined
from google.appengine.ext import db

from models import *

# FACEBOOK_APP_ID = '797761393603664'
# FACEBOOK_APP_SECRET = 'd95c7c45b86a757f44b7c4991a0b7f47'

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
    @property
    def current_user(self):
        cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
        logging.info(cookie)
        if cookie:
            user = User.get_by_key_name(cookie["uid"])
            if not user:
                logging.info("not existing")
                # Not an existing user so get user info
                graph = facebook.GraphAPI(cookie["access_token"])
                profile = graph.get_object("me")
                user = User(
                    key_name=str(profile["id"]),
                    id=str(profile["id"]),
                    name=profile["name"],
                    profile_url=profile["link"],
                    access_token=cookie["access_token"]
                )
                user.put()
            elif user.access_token != cookie["access_token"]:
                user.access_token = cookie["access_token"]
                user.put()
            
            self.session["user"] = dict(
                name=user.name,
                profile_url=user.profile_url,
                id=user.id,
                access_token=user.access_token
            )
            return self.session.get("user")
        else:
            return None

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

class Home(BaseHandler):
    def get(self):
        context = {}
        template = env.get_template('template/home.html')
        self.response.write(template.render(context))

class About(BaseHandler):
    def get(self):
        passage = '''Graduated from Tsinghua University, I'm now a student at Columbia University in the City of New York, pursuing master degree.<br><br>
        Majored in computer science, I've learned various algorithms in various domains and coded a lot. I'm interested in Computer Vision, Artificial Intelligence. But I kinda hate to do any research in a lab, under the pressure that you have to publish any paper each year.<br><br>
        So I'v decided to be a software engineer as my career. Now, I'm concentrating on website building techniques. I've also got several ideas and I'm now working on them. Check it out in my projects.<br><br>
        Besides, I've got a lot of other ideas. I want to realize them all but they require tons of time and many different skills. If you have any interest in any of them, please feel free to contact me.<br><br>
        As a life long dream, I'd like to see a large leap in virtual reality technology which incorporates brain-machine interface. I also want to witness the birth of the real artificial intelligence.<br><br>
        Someone may say that I have too many desires. But as long as I live, I will persist in realizing them.<br><br>
        '''
        context = {'title': 'We want. We live.', 'passage':passage}
        template = env.get_template('template/about.html')
        self.response.write(template.render(context))

class CrazyProjects(BaseHandler):
    def get(self):
        context = {}
        template = env.get_template('template/home.html')
        self.response.write(template.render(context))

class CrazyIdeas(BaseHandler):
    def get(self):
        context = {}
        template = env.get_template('template/home.html')
        self.response.write(template.render(context))

class Contact(BaseHandler):
    def get(self):
        context = {}
        template = env.get_template('template/home.html')
        self.response.write(template.render(context))

class HireMe(BaseHandler):
    def get(self):
        context = {}
        template = env.get_template('template/home.html')
        self.response.write(template.render(context))