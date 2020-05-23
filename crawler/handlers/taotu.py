import re

import pyquery

from ..libs.base import BaseHandler
from ..libs.common import r1


class TaoTu(BaseHandler):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.192td.com/'
        self.table = 'ii_taotu'
        self.rule = {
            # 'append_page_list_url': '/gq/',
            # listinfo-34-%page.html
            'page_url': '/gc/index_%page.html',
            'end_page': 2,
            'start_page': 2,
            'page_rule': {'list': '.piclist li a'},
            'base_url': self.base_url
        }

    def detail_handler(self, task, *args):
        if type(task) == dict:
            task = task.get('url')

        if task.find('gq/huizhan') != -1 or task.find('gq/dm') != -1 or task.find('gq/car/') != -1 or task.find(
                'gq/chinajoy') != -1:
            return None

        html = self.get_html(task)
        html = html.replace('</html>', '').replace('</body>', '')
        doc = pyquery.PyQuery(html)
        all_num = doc('#allnum').text()
        if all_num and int(all_num) < 10:
            return None

        origin_title = doc('.breadnav a').eq(-1).text()
        download_link, pwd = self.get_download_link(doc)
        number = title = ''
        category = r1(r'\[([^\]]+)\]', origin_title, 1, '')
        if category and category.find('ROSI') != -1:
            category = 'ROSI'

        r = re.search(r'([a-zA-Z]+)\.(\d+)', origin_title)
        if r:
            number = r.group(2)
            title = 'NO.{}'.format(number)
        status = 1 if download_link else 0

        if pwd:
            pwd = pwd.replace('密码: ', '')

        data = {'title': title, 'origin_title': origin_title, 'category': category, 'alias': '', 'url': task,
                'download_link': download_link, 'status': status, 'number': number, 'pwd': pwd}
        # print(data)
        self.save(data, data['origin_title'], i=args[0], n=args[1])

    def get_download_link(self, doc):
        elements = doc('.pictext a')
        download_link = ''
        bd_link = ''

        for element in elements.items():
            href = element.attr('href')
            if href.find('567pan') != -1:
                download_link = href
                break
            if href.find('17d') != -1:
                bd_link = href

        if download_link:
            return download_link, ''

        if not download_link and not bd_link:
            return '', ''

        return self.get_download_link_by_bd(bd_link)

    def get_download_link_by_bd(self, url):
        doc = self.doc(url)
        if doc.html().find('百度盘[封号]') != -1:
            return '', ''
        element = doc('table.td_line td')
        pwd = element.eq(7).text()
        download_element = element.eq(9)
        download_link = download_element('a').attr('href')
        return download_link, pwd
