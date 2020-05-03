import json
import re

import pyquery

from .base import BaseCrawler
from ..common import r1, SS_PROXIES


class TaoTu(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.192td.com/'
        self.thread_num = 30
        self.table = 'taotu'
        self.rule = {
            # 'append_page_list_url': 'gq/index.html',
            'page_list_url': 'gq/index_2.html',
            'end_page': 2,
            'start_page': 2,
            'page_rule': {'list': '.piclist li a'},
            'base_url': self.base_url
        }

    def _post_handler(self, task, **kwargs):
        html = self.http.html(task)
        doc = pyquery.PyQuery(html)
        title = doc('.breadnav a').eq(-1).text()
