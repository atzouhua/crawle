from libs.base_client import BaseClient


class YiQiK(BaseClient):

    def __init__(self):
        super().__init__()
        self.rule = {
            'start_url': '/all/book/2_21_0_0_0_0_0_0_%page.html',
            'page_rule': {"list": "div.alltable a.jt"},
            'post_rule': {"title": "h1.tag"},
            'base_url': 'https://www.17k.com'
        }
        self.col = None

    def before_run(self):
        super().before_run()
        # db = self.get_db()
        # self.col = db.get_collection('17k')

    def parse_page(self, response):
        doc = response.doc
        items = doc('div.infoPath a').items()
        path = [item.text() for item in items]
        print(path, response.url)
        return None
