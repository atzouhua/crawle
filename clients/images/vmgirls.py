from libs.base_client import BaseClient
from libs.common import format_url


class VmGirls(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.vmgirls.com'
        self.rule = {
            'page_url': '/page/%page',
            'page_rule': {"list": '.list-home a.list-title', 'title': 'a.list-title'},
            'post_rule': {},
            'base_url': self.base_url,
        }

    def detail_handler(self, task, *args):
        data = super().detail_handler(task, *args)
        if not data:
            return None

        doc = data.get('doc')
        elements = doc('.nc-light-gallery a')
        title = doc('.post-title').text()
        images = []
        for element in elements.items():
            images.append(format_url(element.attr('href'), self.base_url))
        print(title, images)
