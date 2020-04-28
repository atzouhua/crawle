import json

import pyquery

from .base import BaseCrawler
from ..common import format_url, r1


class MkZhan(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.mkzhan.com'
        self.is_update = False
        self.rule = {
            'page_list_url': '/category/?page=%page',
            'end_page': 5,
            'start_page': 1,
            'page_rule': {
                "list": ".common-comic-item .comic__title a",
            },
            'post_rule': {},
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
        data = super(MkZhan, self)._post_handler(task, **kwargs)
        doc = data.get('doc')

        _container = doc('.de-container')
        elements = _container('.chapter__list-box li a')
        book = {
            'title': doc('.j-comic-title').text().strip(),
            'is_finish': 0 if _container('.de-chapter__title span').eq(0).text() == '连载' else 1,
            'thumbnail': doc('.de-info__cover img').attr('data-src'),
            'url': task
        }
        book_items = []
        index = 0
        for element in elements.items():
            index += 1
            book_url = format_url(element.attr('data-hreflink'), self.base_url)
            book_items.append(book_url)

        if len(book_items):
            if self.is_update:
                book_items = book_items[0:3]

            thread_num = 20 if len(book_items) > 100 else 10
            item_result = self.execute(book_items, self._book_item_handler, thread_num=thread_num)
            if item_result and len(item_result):
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
        elements = doc('.rd-article-wr .rd-article__pic img')
        item_name = doc('.last-crumb').text()
        r = r1('^[0-9]*$', item_name, 0)
        if r:
            item_name = '第%s话' % int(item_name)

        images = []
        for element in elements.items():
            image = element.attr('data-src')
            images.append(image)

        if len(images) < 3:
            return None
        return {'name': item_name, 'images': images}
