from views import *

class RTask(BaseHandler):
    def get(self):
        # for cat in Categories:
        arts = Article.query(Article.category=='youmu_blade_dance').order(-Article.date).fetch()
        arts.reverse()
        for i in xrange(0, len(arts)):
            arts[i].category = 'ybd'
        ndb.put_multi(arts)

class UploadRemove(BaseHandler):
    def post(self):
        safe_url = self.request.get('safe_url')
        file_key = blobstore.BlobKey(safe_url)
        images.delete_serving_url(file_key)
        blobstore.BlobInfo(file_key).delete()
        self.response.out.write('success')

class UploadURL(BaseHandler):
    def post(self):
        upload_url = blobstore.create_upload_url(self.uri_for('image_upload'))
        self.response.write(upload_url)

class Upload(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'
        upload = self.get_uploads('image')
        if upload == []:
            self.response.out.write(json.dumps({
                'error': True,
                'message': 'No file.'
            }))
            return

        uploaded_file = upload[0]
        self.response.out.write(json.dumps({
            'safe_url': str(uploaded_file.key()), 
            'url': images.get_serving_url(uploaded_file.key(), size=1000)
        }))

class Edit(BaseHandler):
    def get(self):
        try:
            category = self.request.get('category')
            index = int(self.request.get('index'))
            article = Article.query(Article.category==category, Article.index==index).get()
            context = {
                'title': article.title,
                'content': article.content,
                'date': article.date.strftime("%Y-%m-%d"),
                'category': article.category,
                'id': article.key.id(),
            }
        except Exception, e:
            context = {}

        context['Categories'] = Categories
        logging.info(context)
        self.render('content_edit', context)

    def post(self):
        try:
            article_id = int(self.request.get('id'))
            article = Article.get_by_id(article_id)
        except Exception, e:
            article = None

        title = self.request.get('title')
        date = self.request.get('date')
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        content = self.request.get('content')
        category = self.request.get('category')
        # images = self.request.POST.getall('images[]')
        
        # image_keys = []
        # for i in range(0, len(images)):
        #     file_key = blobstore.BlobKey(images[i])
        #     image_keys.append(file_key)

        if not article:
            prev = Article.query(Article.category==category).order(-Article.date).get()
            if prev:
                index = prev.index + 1
            else:
                index = 1
            article = Article(title=title, content=content, category=category, date=date, index=index)
        else:
            article.title = title
            article.content = content
            article.category = category
            article.date = date
        article.put()

        self.notify('Submit successfully.', 'success')
