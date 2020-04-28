import pyquery

from .base import BaseCrawler
from ..common import SS_PROXIES
from ..utils.db import DB


class Kitty(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.torrentkitty.vip'
        self.proxies = SS_PROXIES

    def run(self):
        data = self.get_task()
        self.execute(data, self.parse_magnet)

    def parse_magnet(self, task, **kwargs):
        html = self.http.html(task)
        doc = pyquery.PyQuery(html)
        elements = doc('#archiveResult tr a[rel="information"]')
        information = []
        for element in elements.items():
            information.append('{}{}'.format(self.base_url, element.attr('href')))
        data = self.execute(information, self.find_magnet, **kwargs)

        status = 2
        magnet_link = ''
        if data:
            data.sort(key=lambda k: k[0])
            kwargs['url'] = data[0][2]
            kwargs.setdefault('magnet_link', data[0][1])
            status = 1
            magnet_link = data[0][1]

        print('{} {}'.format(kwargs.get('alias'), magnet_link))
        DB.update('ii_mgstage', {'status': status, 'magnet_link': magnet_link}, 'id = {}'.format(kwargs['id']))
        return kwargs

    def find_magnet(self, task, **kwargs):
        html = self.http.html(task)
        doc = pyquery.PyQuery(html)
        elements = doc('#torrentDetail tr')
        n = len(elements)
        alias = kwargs.get('alias')
        for element in elements.items():
            _name = element('td.name').text()
            if not _name:
                continue
            if _name.find(alias) != -1 and _name.find('jpg') == -1:
                return n, doc('.magnet-link').text(), task
        return None

    def get_task(self):
        sql = 'select id, `alias`, publish_time from ii_mgstage where status = 0 order by publish_time desc limit 30'
        data = DB.all(sql)
        task_list = []
        for item in data:
            alias = item['alias']
            search_url = '{}/search/{}/'.format(self.base_url, alias)
            task_list.append({'url': search_url, 'alias': alias, 'id': item['id']})
        return task_list
