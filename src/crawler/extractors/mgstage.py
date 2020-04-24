import json
import re
from urllib.parse import urlencode

from .base import BaseCrawler
from ..common import r1
from ..utils.db import DB

IMAGE_WORD_LIST = ['nanpatv', 'documentv', 'ara', 'prestigepremium', 'luxutv', 'dokikaku',
                   'orenoshirouto', 'scute', 'shirouto']


class MgStage(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.mgstage.com'
        self.rule = {
            'page_list_url': '/search/search.php?search_word=&{}&sort=new&list_cnt=120&disp_type=thumb&page=%page'.format(
                urlencode({'image_word_ids[]': IMAGE_WORD_LIST}, doseq=True)),
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
        params = {
            'publish_time': r1(r'<td>(\d{4}/\d{1,2}/\d{1,2})</td>', doc.html()).replace('/', '-'),
            'alias': task.strip('/').split('/')[-1],
            'thumbnail': doc('#EnlargeImage').attr('href'),
            'images': json.dumps(self._get_images(doc)),
            'url': data['url'],
            'title': data['title'],
        }
        del data

        self.processing(kwargs.get('bar'), params['alias'], 'done')
        self.data.append(params)
        if len(self.data) > 50:
            DB.insert_all('ii_mgstage', self.data)
            self.data = []

    @staticmethod
    def _get_images(doc):
        elements = doc('a.sample_image')
        image_list = []
        for element in elements.items():
            image_list.append(element.attr('href'))

        if len(image_list) < 5:
            end_image = image_list[-1]
            num = int(re.search(r'cap_e_(\d+)_', end_image).group(1))
            for i in range(num, num + 6):
                image = re.sub(r'cap_e_(\d+)_', 'cap_e_{}_'.format(i), end_image)
                image_list.append(image)

        return image_list
