import base64
import json
import re
from concurrent.futures import Future

import pyquery

from src.crawler.extractors import BaseProvider
from src.crawler.utils.common import format_url
from src.crawler.utils.config import get_config


class Qq(BaseProvider):

    def __init__(self):
        BaseProvider.__init__(self)
        self.base_url = 'https://ac.qq.com'
        self.update_url = '/update'
        self.page_list_url = '/Comic/all/nation/1/search/time/vip/1/page/%page'
        self.end_page = 1
        self.rule.config = {
            'page_rule': {
                "list": ".ret-search-list li .ret-works-info",
                "url": " .ret-works-title a",
            },
            'base_url': self.base_url
        }

    def future_callback_parse_post(self, future: Future):
        result = future.result()
        return self.parse_book(result[0], **result[1])

    def do_book(self, **kwargs):
        kwargs.setdefault('i', 1)
        kwargs.setdefault('n', 1)
        html = self.get_html(get_config('url'))
        return self.parse_book(html, **kwargs)

    def parse_book(self, html, **kwargs):
        doc = pyquery.PyQuery(html)
        container = doc('.works-intro-wr')
        elements = doc('.chapter-page-all a')
        item = {
            'title': container('.works-intro-title').text(),
            'is_finish': 1 if container('.works-intro-status').text() == '连载中' else 2,
            'thumbnail': container('.works-cover img').attr('src')}
        book_item_tasks = []
        index = 0
        for element in elements.items():
            index += 1
            book_url = format_url(element.attr('href'), self.base_url)
            book_item_tasks.append(book_url)
            if kwargs.get('is_update') and index >= 5:
                break

        print(self.parse_book_item(book_item_tasks[0]))
        self.processing(kwargs.get('bar'), item.get('title'))

        self.data.append(item)
        return item

    def parse_book_item(self, task, **kwargs):
        html = self.get_html(task)
        # r = re.search('url\s*=\s*"(.+)"', html)
        # if r:
        #     return r.group(1)
        return self.parser_book_image(html)

    def parser_book_image(self, html):
        CHAPTER_JSON_STR_PATTERN = re.compile('("chapter":{.*)')
        bs64_data = re.search("var DATA\s*=\s*'(.*?)'", html).group(1)
        for i in range(len(bs64_data)):
            try:
                json_str_part = base64.b64decode(bs64_data[i:]).decode('utf-8')
                break
            except Exception:
                pass
        else:
            raise

        json_str = "{" + CHAPTER_JSON_STR_PATTERN.search(json_str_part).group(1)
        res = json.loads(json_str)
        images = []
        for i in res.get('picture'):
            images.append(i.get('url'))
        return images
