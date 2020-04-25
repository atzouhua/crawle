import json
import re

import pyquery

from .base import BaseCrawler
from ..common import r1, SS_PROXIES
from ..utils.db import DB

TAGS = ['処女', '女捜査官', '痴女', '家庭教師', '妊婦', '美脚', '風俗', '美尻', '巨乳', '美乳', '女医', '乱交', '顔射', '女教師', '淫語',
        '異物挿入', '母乳', 'SM', '巨尻', '鬼畜', '監禁', '熟女', 'SF', '制服', '痴漢', 'VR', '素人', '爆乳', '美少女', '人妻', '泥酔', '騎乗位',
        '口内発射', '女子校生', '女子大生', '不倫', '巫女', '近親相姦', '食糞']


class MgStage(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://mgstage.atcaoyufei.workers.dev/'
        self.thread_num = 20
        self.proxies = SS_PROXIES
        self.rule = {
            'page_list_url': '/search/search.php?search_word=&sort=new&list_cnt=120&disp_type=thumb&page=%page',
            'end_page': 1,
            'start_page': 1,
            'page_rule': {"list": "div.rank_list li h5 a"},
            'post_rule': {"title": "h1.tag"},
            'base_url': self.base_url
        }

    def before_run(self):
        super(MgStage, self).before_run()
        self.http.request.cookies.set('adc', '1')

    def _post_handler(self, task, **kwargs):
        data = super(MgStage, self)._post_handler(task, **kwargs)
        doc = data.get('doc')
        star, tag = _get_star_tag(doc)
        images = _get_images(doc)

        params = {
            'publish_time': r1(r'(\d{4}/\d{1,2}/\d{1,2})', doc.html()).replace('/', '-'),
            'alias': task.strip('/').split('/')[-1],
            'thumbnail': doc('#EnlargeImage').attr('href'),
            'images': json.dumps(images),
            'url': data['url'],
            'title': _format_title(data['title']),
            'star': star,
            'tag': tag
        }
        del data

        if not images:
            self.processing(kwargs.get('bar'), params['alias'], 'fail')
            return

        self.processing(kwargs.get('bar'), params['alias'], 'done')
        self.data.append(params)
        if len(self.data) >= 50:
            DB.insert_all('ii_mgstage', self.data)
            self.data = []

    def after_run(self):
        if len(self.data):
            DB.insert_all('ii_mgstage', self.data)
            self.data = []

    def _get_makes(self):
        html = self.http.html('https://www.mgstage.com/ppv/makers.php')
        doc = pyquery.PyQuery(html)
        elements = doc('.maker_list_box a')
        data = []
        for element in elements.items():
            href = element.attr('href')
            href = r1('=(.+)', href)
            data.append(href)

        data = list(set(data))
        print(data)
        print(len(data))

    def get_tag(self):
        html = self.http.html('https://www.mgstage.com/ppv/genres.php')
        doc = pyquery.PyQuery(html)
        elements = doc('#genres_list a')
        data = []
        for element in elements.items():
            tag = element.text()
            r = re.search('[\u0800-\u4e00]', tag)
            if not r:
                data.append(tag)
        print(list(set(data)))
        exit()


def _format_title(title):
    n = title.find('公開日')
    if n == -1:
        return title
    return title[0: n].strip()


def _get_images(doc):
    elements = doc('a.sample_image')
    if not len(elements):
        return None

    image_list = []
    for element in elements.items():
        image_list.append(element.attr('href'))

    n = len(image_list)
    if n > 10:
        return image_list[0:10]

    if n and n < 5:
        end_image = image_list[-1]
        num = int(re.search(r'cap_e_(\d+)_', end_image).group(1))
        for i in range(num, num + 6):
            image = re.sub(r'cap_e_(\d+)_', 'cap_e_{}_'.format(i), end_image)
            image_list.append(image)
    return image_list


def _get_star_tag(doc):
    elements = doc('.detail_txt li')
    tags = []
    if len(elements):
        return _star_tag(elements)
    else:
        element_tables = doc('table')
        for element_table in element_tables.items():
            html = element_table.html()
            if html.find('ジャンル') != -1:
                element_trs = element_table('table tr')
                return _star_tag(element_trs)
    return json.dumps([], ensure_ascii=False), json.dumps(tags)


def _star_tag(elements):
    star = ''
    tags = []
    for element in elements.items():
        text = element.text()
        if text.find('出演') != -1:
            _star = element('td').text()
            r = re.search('([0-9]+)', _star)
            if not r:
                star = _star

        if text.find('ジャンル') != -1:
            tag_elements = element('a')
            for tag_element in tag_elements.items():
                tag = tag_element.text()
                if tag in TAGS:
                    tags.append(tag)
    if star:
        star = star.split(' ')
    else:
        star = []
    return json.dumps(star, ensure_ascii=False), json.dumps(tags, ensure_ascii=False)
