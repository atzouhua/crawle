import json
import re

from libs.base_client import BaseClient
from libs.common import r1


class Mgstage(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.mgstage.com/'
        self.rule = {
            'start_url': '/search/search.php?search_word=&sort=new&list_cnt=30&disp_type=thumb&page=%page',
            'page_rule': {"list": "div.rank_list li h5 a"},
            'post_rule': {"title": "h1.tag"},
            'base_url': self.base_url
        }

    def before_run(self):
        super().before_run()
        self.session.cookies.set('adc', '1')

    def parse_page(self, response):
        doc = response.doc
        star, tag = _get_star_tag(doc)
        images = _get_images(doc)
        title = doc('h1.tag').text()
        publish_time = r1(r'(\d{4}/\d{1,2}/\d{1,2})', doc.html())
        if publish_time:
            publish_time = publish_time.replace('/', '-')

        params = {
            'publish_time': publish_time,
            'alias': response.url.strip('/').split('/')[-1],
            'thumbnail': doc('#EnlargeImage').attr('href'),
            'images': images,
            'title': _format_title(title),
            'star': star,
            'tag': tag
        }
        self.logger.info(f"{response.index}/{response.total}: {params['alias']}.")
        return params

    def save(self, data):
        self.do_save(data, 'mgstage')

    def _get_makes(self):
        doc = self.doc('https://www.mgstage.com/ppv/makers.php')
        elements = doc('.maker_list_box a')
        data = []
        for element in elements.items():
            href = element.attr('href')
            href = r1('=(.+)', href)
            data.append(href)

        data = list(set(data))
        print(data)
        print(len(data))


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
    if n and n < 5:
        end_image = image_list[-1]
        num = int(re.search(r'cap_e_(\d+)_', end_image).group(1))
        for i in range(num, num + 6):
            image = re.sub(r'cap_e_(\d+)_', 'cap_e_{}_'.format(i), end_image)
            image_list.append(image)
    return image_list


def _get_star_tag(doc):
    elements = doc('.detail_txt li')
    if len(elements):
        return _star_tag(elements)

    element_trs = doc('.detail_data table tr')
    return _star_tag(element_trs)
    # return json.dumps([], ensure_ascii=False), json.dumps(tags)


def _star_tag(elements):
    star = ''
    tags = []
    for element in elements.items():
        text = element.text()
        if text.find('出演') != -1:
            star = element('td').text().strip()
            continue

        if text.find('ジャンル') != -1:
            tag_elements = element('a')
            for tag_element in tag_elements.items():
                tag = tag_element.text().strip()
                if tag not in ['配信専用', '独占配信', '単体作品', '主観'] and '上作品' not in tag:
                    tags.append(tag)
    if star:
        r = re.search(r'(\d+)歳', star)
        star = star.split(' ')
        if r:
            star = [star[0]]
    else:
        star = []
    return star, tags
