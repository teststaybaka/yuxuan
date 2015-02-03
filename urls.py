import webapp2
import views


config = {}
config['webapp2_extras.sessions'] = dict(secret_key='efrgdjcmzlworj79s0mgnvdoifds68dkxmc97jvdkmvzxp027yutcivbhugd479k')#, session_max_age=5)
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/about', views.About, name='about'),
    webapp2.Route(r'/contact', views.Contact, name='contact'),
    webapp2.Route(r'/hire_me', views.HireMe, name='hire_me'),
    webapp2.Route(r'/crazy_projects', views.CrazyProjects, name='crazy_projects'),
    webapp2.Route(r'/crazy_ideas', views.CrazyIdeas, name='crazy_ideas'),
], debug=True
, config=config)
