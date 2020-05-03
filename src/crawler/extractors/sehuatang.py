import base64
import json
import re

import pyquery

from .base import BaseCrawler
from ..common import format_url, r1, SS_PROXIES


class SeHuaTang(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.sehuatang.net'
        self.is_update = False
        self.rule = {
            'page_list_url': 'forum.php?mod=forumdisplay&fid=%cid&page=%page',
            'end_page': 1,
            'start_page': 1,
            'base_url': self.base_url
        }
        self.proxies = SS_PROXIES
        self.table = 'sehuatang'

    def action_test(self):
        print(self._get_image('dnjr-027'))

    def _index_handler(self, url: str, **kwargs) -> list:
        self.logger.info('[%s/%s] Get page: %s' % (kwargs.get('i'), kwargs.get('n'), url))
        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        body_elements = doc('#threadlisttableid tbody')
        result = []
        for element in body_elements.items():
            body_id = element.attr('id')
            if not body_id or body_id.find('normalthread') == -1:
                continue

            a_element = element('a.s')
            url = format_url(a_element.attr('href'), self.base_url)
            title = a_element.text()
            result.append({'title': title, 'url': url, 'thumbnail': ''})
        return result

    def _post_handler(self, task, **kwargs):
        html = self.http.html(task)
        doc = pyquery.PyQuery(html)
        element = doc('.blockcode li')
        title = kwargs.get('title', doc('#thread_subject').text())
        magnet_link = element.text()
        alias = r1(r'([a-zA-z0-9-]+-[0-9]+)', title)
        thumbnail = ''
        star = images = []
        if alias:
            thumbnail, images, star = self._get_image(alias)
            if len(images) > 10:
                images = images[0:10]

        params = {'alias': alias, 'thumbnail': thumbnail, 'images': json.dumps(images), 'url': task, 'title': title,
                  'star': json.dumps(star), 'magnet_link': magnet_link
                  }
        self.save(params, 'alias', **kwargs)

    def _get_image(self, alias):
        try:
            html = self.http.html('https://www.busdmm.one/{}'.format(alias))
            doc = pyquery.PyQuery(html)
            thumbnail = doc('.bigImage').attr('href')
            elements = doc('#sample-waterfall a')
            images = []
            for element in elements.items():
                images.append(element.attr('href'))
            star_elements = doc('.star-name a')
            star_list = []
            for element in star_elements.items():
                star_list.append(element.text())
            return thumbnail, images, star_list
        except Exception as e:
            html = self.http.html('http://www.jav321.com/search', {'sn': alias})
            doc = pyquery.PyQuery(html)
            elements = doc('.row .col-md-3 .col-xs-12 a img')
            images = []
            for element in elements.items():
                images.append(element.attr('src'))
            if images:
                return images[0], images[1:], []
            return '', [], []
