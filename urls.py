import webapp2
import views, admin


config = {}
application = webapp2.WSGIApplication([
    webapp2.Route(r'/', views.Home, name='home'),
    webapp2.Route(r'/about', views.About, name='about'),
    webapp2.Route(r'/contact', views.Contact, name='contact'),
    webapp2.Route(r'/send_email', views.SendEmail, name='send_email'),

    webapp2.Route(r'/admin/edit', admin.Edit, name="content_edit"),
    webapp2.Route(r'/admin/task', admin.RTask, name="random_task"),
    webapp2.Route(r'/image_upload', admin.Upload, name="image_upload"),
    webapp2.Route(r'/upload_url', admin.UploadURL, name="upload_url"),
    webapp2.Route(r'/image_remove', admin.UploadRemove, name="image_remove"),

    webapp2.Route(r'/<category:.+>/<index:\d+>', views.PerArticle, name='perarticle'),
    webapp2.Route(r'/<category:.+>', views.Articles, name='articles'),
], debug=True
, config=config)
