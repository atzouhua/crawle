import json
import random

from ..libs.base import BaseHandler
from ..libs.common import format_url, get_item_name, format_view


class MkZhan(BaseHandler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.mkzhan.com'
        self.publish_url = 'http://hahamh.me'
        self.is_update = False
        self.rule = {
            'page_url': '/category/?page=%page',
            'end_page': 5,
            'start_page': 1,
            'page_rule': {'list': '.common-comic-item .comic__title a'},
            'post_rule': {},
            'base_url': self.base_url
        }
        if not self.proxies:
            self.publish_url = 'http://www.hahamh.net'

    def before_run(self):
        self.proxies = None

    def action_update(self):
        self.is_update = True
        self.rule['page_rule'] = {'list': ".update-list.active .common-comic-item .comic__title a"}
        _url = format_url('/update', self.base_url)
        result = self.page_handler(_url, 1, 1)
        self.crawl([result[0]], self.detail_handler)

    def action_banner(self):
        doc = self.doc(self.base_url)
        elements = doc('.in-banner img')
        banners = []
        for element in elements.items():
            src = element.attr('data-src')
            if str(src).endswith('banner-600'):
                name = element.attr('alt')
                banners.append({'name': name, 'src': src})
        data = {'banners': json.dumps(banners, ensure_ascii=False)}
        res = self.get_html(format_url('/api/banner', self.publish_url), data=data)
        print(res)

    def detail_handler(self, task, *args):
        doc = self.doc(task)
        book = self._get_book_params(doc)
        res = self.get_html(format_url('/api/post-save', self.publish_url), data=book)
        self.processing(args[0], args[1], '{}: publish: {}'.format(book['title'], res))
        return book

    def _get_book_params(self, doc):
        _container = doc('.de-container')

        book = {
            'title': doc('.j-comic-title').text().strip(),
            'is_finish': 0 if _container('.de-chapter__title span').eq(0).text() == '连载' else 1,
            'is_new': 0 if self.is_update else 1
        }
        if not self.is_update:
            score = int(doc('.rate-handle').attr('data-score')) / 10
            if score > 10:
                score = '9.%s' % random.randint(1, 8)

            book['thumbnail'] = doc('.de-info__cover img').attr('data-src')
            book['description'] = doc('.intro').text()
            book['view_count'] = format_view(doc('.comic-status .text b').eq(2).text())
            book['tag'] = doc('.comic-status .text b').eq(0).text().replace(' ', ',')
            book['score'] = score
            book['author'] = doc('.comic-author .name').text()
        book.update(self._get_book_item_params(_container))
        return book

    def _get_book_item_params(self, _container):
        elements = _container('.chapter__list-box li a')
        book_items = []
        for element in elements.items():
            book_url = format_url(element.attr('data-hreflink'), self.base_url)
            book_items.append(book_url)

        n = len(book_items)
        params = {}
        if n:
            thread_num = max(20, n)
            if self.is_update:
                book_items = book_items[0:3]
                thread_num = 3

            self.sess = self.get_new_request_session()
            item_result = self.crawl(book_items, self.item_handler, thread_num)
            if item_result and len(item_result):
                params['last_item'] = item_result[-1].get('name')
                params['items'] = json.dumps(item_result, ensure_ascii=False)
        return params

    def item_handler(self, task, *args):
        doc = self.doc(task, session=self.sess)
        elements = doc('.rd-article-wr .rd-article__pic img')
        item_name = doc('.last-crumb').text()
        item_name = get_item_name(item_name).replace('“', '').replace('”', '')

        images = []
        for element in elements.items():
            image = element.attr('data-src')
            images.append(image)

        if len(images) < 3:
            return None
        return {'name': item_name, 'images': images}
