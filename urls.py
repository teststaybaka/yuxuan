import webapp2
import views, admin


config = {}
config['webapp2_extras.sessions'] = dict(secret_key='efrgdjcmzlworj79s0mgnvdoifds68dkxmc97jvdkmvzxp027yutcivbhugd479k')#, session_max_age=5)
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/about', views.About, name='about'),
    webapp2.Route(r'/contact', views.Contact, name='contact'),
    webapp2.Route(r'/hire_me', views.HireMe, name='hire_me'),
    webapp2.Route(r'/projects', views.Projects, name='projects'),
    webapp2.Route(r'/ideas', views.Ideas, name='ideas'),
    webapp2.Route(r'/send_email', views.SendEmail, name='send_email'),

    webapp2.Route(r'/admin/edit', admin.Edit, name="content_edit"),
    webapp2.Route(r'/image_upload', admin.Upload, name="image_upload"),
    webapp2.Route(r'/upload_url', admin.UploadURL, name="upload_url"),
    webapp2.Route(r'/image_remove', admin.UploadRemove, name="image_remove"),
], debug=True
, config=config)
