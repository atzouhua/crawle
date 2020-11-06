from libs.base_client import BaseClient


class BaseBook(BaseClient):

    def __init__(self):
        super(BaseBook, self).__init__()
        self.publish_url = 'http://hahamh.me/api/post-save' if self.dev_env else 'https://api.mh01.net/api/post-save'

