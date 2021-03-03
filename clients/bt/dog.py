from libs.base_client import BaseClient
from libs.common import format_url


class Dog(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://dog.g57h.xyz'
        self.rule = {
            'start_url': '/search/%E5%B9%BB%E6%83%B3%E4%B9%90%E5%9B%AD/1/%page',
            'page_rule': {"list": 'h5.item-title a'},
            'post_rule': {},
            'base_url': self.base_url,
        }
        self.file = open('magnet_link.txt', 'w+', encoding='utf-8')

    def parse_page(self, response):
        doc = response.doc
        magnet_link = doc('#MagnetLink').text()
        title = doc('.div-search-box').text()
        self.file.write(f'{magnet_link}\n')
        self.logger.info(f"[{response.index}/{response.total}]:{title}")
