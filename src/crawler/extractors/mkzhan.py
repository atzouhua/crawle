import json

import pyquery

from src.crawler.extractors import BaseProvider
from src.crawler.utils.common import format_url, get_book_item_name


class Mkzhan(BaseProvider):

    def __init__(self):
        BaseProvider.__init__(self)
        self.base_url = 'https://www.mkzhan.com'
        self.publish_api = 'http://api.hahamh.net/api/post-save'
        self.update_url = '/update'
        self.rule = {
            'page_list_url': '/category/?page=%page',
            'end_page': 5,
            'page_rule': {
                "list": ".cate-comic-list .common-comic-item",
                "url": " .comic__title a",
            },
            'base_url': self.base_url
        }

    def run(self):
        self.proxies = None
        super().run()

    def action_update(self, **kwargs):
        _url = format_url(self.update_url, self.base_url)
        self.rule['page_rule'] = {
            'list': ".update-list.active .common-comic-item",
            'url': ".comic__title a",
        }
        kwargs.setdefault('i', 1)
        kwargs.setdefault('n', 1)
        kwargs.setdefault('is_update', True)
        return self._index_handler(_url, **kwargs)

    def _post_handler(self, url, **kwargs):
        # self.logger.info('[%s/%s] parse book: %s' % (kwargs.get('i'), kwargs.get('n'), book_url))
        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        _container = doc('.de-container')
        elements = _container('.chapter__list-box li a')
        book = {
            'title': doc('.j-comic-title').text().strip(),
            'is_finish': 1 if _container('.de-chapter__title span').eq(0).text() == '连载' else 2,
            'thumbnail': doc('.de-info__cover img').attr('data-src')
        }
        _book_items = []
        index = 0
        for element in elements.items():
            index += 1
            book_url = format_url(element.attr('data-hreflink'), self.base_url)
            _book_items.append(book_url)
            if kwargs.get('is_update') and index >= 5:
                break

        if len(_book_items):
            thread_num = 20 if len(_book_items) > 100 else 10
            item_result = self.execute(_book_items, self._book_item_handler, thread_num=thread_num)
            if len(item_result):
                book['last_item'] = item_result[0].get('name')
                book['items'] = json.dumps(item_result, ensure_ascii=False)

        # res = self.publish(item)
        #
        self.processing(kwargs.get('bar'), book.get('title'), 'done')
        #
        # self.data.append(item)
        return book

    def _book_item_handler(self, book_item_url, **kwargs):
        html = self.http.html(book_item_url)
        doc = pyquery.PyQuery(html)
        elements = doc('.rd-article-wr .rd-article__pic img')
        item_name = doc('.last-crumb').text()
        item_name = get_book_item_name(item_name)
        images = []
        for element in elements.items():
            image = element.attr('data-src')
            images.append(image)
        return {'name': item_name, 'images': images}
