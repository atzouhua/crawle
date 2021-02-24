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

    def action_index(self):
        doc = self.doc(f'{self.base_url}/archives.html')
        elements = doc('.archives a')
        url_list = []
        for element in elements.items():
            url_list.append(f"{self.base_url}/{element.attr('href')}")
        self.crawl(url_list[0:10], self.detail_handler, 5)

    def detail_handler(self, task, *args):
        doc = self.doc(task)
        elements = doc('.nc-light-gallery a')
        title = doc('.post-title').text()
        images = []
        for element in elements.items():
            images.append(format_url(element.attr('href'), self.base_url))

        tag_list = []
        for element in doc('.post-tags a').items():
            tag_list.append(element.text())
        print(task, title, tag_list)
