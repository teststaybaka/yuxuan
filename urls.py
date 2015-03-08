import webapp2
import views, admin


config = {}
config['webapp2_extras.sessions'] = dict(secret_key='efrgdjcmzlworj79s0mgnvdoifds68dkxmc97jvdkmvzxp027yutcivbhugd479k')#, session_max_age=5)
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/about', views.About, name='about'),
    webapp2.Route(r'/contact', views.Contact, name='contact'),
    webapp2.Route(r'/send_email', views.SendEmail, name='send_email'),
    webapp2.Route(r'/hire_me', views.HireMe, name='hire_me'),
    
    webapp2.Route(r'/ideas', views.Projects, name='projects'),
    webapp2.Route(r'/ideas/dantube', views.DanTube, name='dantube'),
    webapp2.Route(r'/ideas/youmu-blade-dance', views.ActionGame, name='action_game'),

    webapp2.Route(r'/journey', views.Experiences, name='experiences'),
    webapp2.Route(r'/journey/<category:.+>', views.PerExperience, name='experience'),
    webapp2.Route(r'/article/<record_id:\d+>', views.Record, name='record'),
    webapp2.Route(r'/comment/<record_id:\d+>', views.CommentPost, name='comment_post'),

    webapp2.Route(r'/admin/edit', admin.Edit, name="content_edit"),
    webapp2.Route(r'/image_upload', admin.Upload, name="image_upload"),
    webapp2.Route(r'/upload_url', admin.UploadURL, name="upload_url"),
    webapp2.Route(r'/image_remove', admin.UploadRemove, name="image_remove"),
], debug=True
, config=config)
