import re

import pyquery

from ..libs.base import BaseHandler


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

        html = self.get_html(task)
        html = html.replace('</html>', '').replace('</body>', '')
        doc = pyquery.PyQuery(html)
        title = doc('.breadnav a').eq(-1).text()
        download_link, pwd = self.get_download_link(doc)
        number = ''

        r = re.search(r'([a-zA-Z]+)\.(\d+)', title)
        if r:
            number = r.group(2)
            title = 'ROSI NO.{}'.format(number)
        status = 1 if download_link else 0

        data = {'title': title, 'category': 'ROSI', 'alias': 'rosi', 'url': task,
                'download_link': download_link, 'status': status, 'number': number, 'pwd': pwd}
        self.save(data, i=args[0], n=args[1])

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
        element = doc('table.td_line td')
        pwd = element.eq(7).text()
        if pwd:
            pwd.replace('密码: ', '')
        download_element = element.eq(9)
        download_link = download_element('a').attr('href')
        return download_link, pwd
