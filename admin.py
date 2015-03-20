from views import *

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
            article_key = Article.query(Article.category==category).order(-Article.date).fetch(keys_only=True, offset=index-1, limit=1)
            article = article_key[0].get()
            context = {
                'content': article.content,
                'title': article.title,
            }
        except Exception, e:
            context = {}

        self.render('content_edit', context)

    def post(self):
        title = self.request.get('title')
        date = self.request.get('date')
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        content = self.request.get('content')
        category = self.request.get('category')
        # images = self.request.POST.getall('images[]')
        logging.info(type(date))
        
        # image_keys = []
        # for i in range(0, len(images)):
        #     file_key = blobstore.BlobKey(images[i])
        #     image_keys.append(file_key)

        article = Article(title=title, content=content, category=category, date=date)
        article.put()
        self.notify('Submit successfully.', 'success')
