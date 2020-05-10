import json
import re

import pyquery

from ..common import format_url
from .base import BaseCrawler


class Zymk(BaseCrawler):

    def __init__(self):
        super(Zymk, self).__init__()
        self.base_url = 'https://www.zymk.cn'
        self.publish_api = 'http://hahamh.me:8080/api/banner'
        self.update_url = '/update'
        self.proxies = None

    def run(self):
        self.proxies = None
        super().run()

    def action_banner(self, **kwargs):
        self.post_handler = self._banner_handler
        html = self.http.html(self.base_url)
        doc = pyquery.PyQuery(html)
        elements = doc('.superSlide.full-screen li a')
        url_list = []
        for element in elements.items():
            url = format_url(element.attr('href'), self.base_url)
            name = element.attr('title')
            thumbnail = element('img').attr('data-src')
            params = {'thumbnail': thumbnail, 'description': name, 'url': url}
            url_list.append(params)
        return url_list

    def _banner_handler(self, task, **kwargs):
        html = self.http.html(task)
        doc = pyquery.PyQuery(html)
        title = doc('.title-warper .title').text()
        params = {'thumbnail': kwargs.get('thumbnail'), 'description': kwargs.get('description'), 'title':  title}

        res = self.publish(params)
        print(res)
        # self.processing(kwargs.get('bar'), json.dumps(res), 'done')

    def do_update(self, **kwargs):
        task = format_url(self.update_url, self.base_url)
        self.rule = {
            'page_rule': {
                "list": ".update-list.active .common-comic-item",
                "url": " .comic__title a",
            },
        }
        result = self._parse_page(task, **kwargs)
        if len(result):
            kwargs.setdefault('is_update', True)
            self.execute(result, self.parse_book, **kwargs)
        return result

    def do_update_book(self, **kwargs):
        kwargs.setdefault('i', 1)
        kwargs.setdefault('n', 1)
        kwargs.setdefault('is_update', True)
        return self.parse_book(kwargs.get('url'), **kwargs)

    def parse_book(self, task, **kwargs):
        # self.logger.info('[%s/%s] parse book: %s' % (kwargs.get('i'), kwargs.get('n'), task))
        html = self.get_html(task)
        doc = pyquery.PyQuery(html)
        container = doc('.de-container')
        elements = container('.chapter__list-box li a')
        item = {
            'title': doc('.j-comic-title').text(),
            'is_finish': 1 if container('.de-chapter__title span').eq(0).text() == '连载' else 2,
            'thumbnail': doc('.de-info__cover img').attr('data-src')}
        book_item_tasks = []
        index = 0
        for element in elements.items():
            index += 1
            book_url = format_url(element.attr('data-hreflink'), self.base_url)
            book_item_tasks.append(book_url)
            if kwargs.get('is_update') and index >= 5:
                break

        if len(book_item_tasks):
            item_result = self.execute(book_item_tasks, self.parse_book_item)
            if len(item_result):
                item['last_item'] = item_result[0].get('name')
                item['items'] = json.dumps(item_result, ensure_ascii=False)
                # item['items'] = item_result
        html = self.get_html(self.publish_api, item)
        # FileHelper.write_file('mkzhan.json', json.dumps(item, ensure_ascii=False))
        return html

    def parse_book_item(self, task, **kwargs):
        self.logger.info('[%s/%s] parse book item: %s' % (kwargs.get('i'), kwargs.get('n'), task))
        html = self.get_html(task)
        doc = pyquery.PyQuery(html)
        elements = doc('.rd-article-wr .rd-article__pic img')
        item_name = doc('.last-crumb').text()
        item_name = self.format_name(item_name)
        images = []
        for element in elements.items():
            image = element.attr('data-src')
            images.append(image)
        return {'name': item_name, 'images': images}

    def format_name(self, item_name):
        s = re.search('^[0-9]*$', item_name)
        if s:
            item_name = '第%s话' % item_name
        return item_name
