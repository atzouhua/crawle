import base64
import json
import re

import pyquery

from ..libs.base_client import BaseClient
from ..libs.common import format_url, r1


class AcQQ(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://ac.qq.com'
        self.is_update = False
        self.rule = {
            'page_url': '/Comic/all/search/time/vip/1/page/%page',
            'end_page': 1,
            'start_page': 1,
            'page_rule': {'list': '.ret-search-list li .ret-works-cover a.mod-cover-list-thumb'},
            'post_rule': {'title': '.works-intro-title', 'thumbnail': '.works-cover img'},
            'base_url': self.base_url
        }

    def action_update(self, **kwargs):
        self.is_update = True
        self.rule['page_rule'] = {'list': ".update-list.active .common-comic-item .comic__title a"}
        _url = format_url('/update', self.base_url)
        kwargs.setdefault('i', 1)
        kwargs.setdefault('n', 1)
        result = self._index_handler(_url, **kwargs)
        self.after_index(result)

    def _post_handler(self, task, **kwargs):
        # self.logger.info('[%s/%s] parse book: %s' % (kwargs.get('i'), kwargs.get('n'), book_url))
        data = super(AcQQ, self)._post_handler(task, **kwargs)
        doc = data.get('doc')

        book = {
            'title': data['title'],
            'is_finish': 0 if doc('.works-intro-status').eq(0).text() == '连载中' else 1,
            'thumbnail': data['thumbnail'],
            'url': task,
            'author': doc('.works-author-name').text(),
            'description': doc('.works-intro-short').text(),
        }
        book_items = []
        index = 0

        elements = doc('.chapter-page-all a')
        for element in elements.items():
            index += 1
            book_item_url = format_url(element.attr('href'), self.base_url)
            book_items.append(book_item_url)

        if len(book_items):
            if self.is_update:
                book_items = book_items[0:3]

            thread_num = 20 if len(book_items) > 100 else 10
            item_result = self.execute(book_items, self._book_item_handler, thread_num=thread_num)
            if item_result and len(item_result):
                item_result.reverse()
                book['last_item'] = item_result[-1].get('name')
                book['items'] = json.dumps(item_result, ensure_ascii=False)

        print(book)
        # res = self.publish(item)
        #
        # self.processing(kwargs.get('bar'), book.get('title'), 'done')
        #
        # self.data.append(item)
        # return book

    def _book_item_handler(self, book_item_url, **kwargs):
        html = self.http.html(book_item_url)
        doc = pyquery.PyQuery(html)
        item_name = doc('#comicTitle .title-comicHeading').text()
        r = r1('^[0-9]*$', item_name, 0)
        if r:
            item_name = '第%s话' % int(item_name)

        images = parser_book_image(html)
        return {'name': item_name, 'images': images}


def parser_book_image(html):
    chapter_json_str_pattern = re.compile('("chapter":{.*)')
    bs64_data = re.search(r"\sDATA\s*=\s*'([^']{32,})'", html).group(1)
    for i in range(len(bs64_data)):
        try:
            json_str_part = base64.b64decode(bs64_data[i:]).decode('utf-8')
            break
        except Exception:
            pass
    else:
        return None

    json_str = "{" + chapter_json_str_pattern.search(json_str_part).group(1)
    res = json.loads(json_str)
    images = []
    for i in res.get('picture'):
        images.append(i.get('url'))
    return images
