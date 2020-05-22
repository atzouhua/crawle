import re
from urllib import parse

from ..libs.base import BaseHandler
from ..libs.common import r2, r1


class SouSi(BaseHandler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.sosi55.com'
        self.rule = {
            'page_url': '/guochantaotu/list_22_%page.html',
            'end_page': 1,
            'start_page': 1,
            'page_rule': {"list": '.yuanma_downlist_box .pic a'},
            'post_rule': {'title': '.single h1'},
            'base_url': self.base_url
        }
        self.charset = 'gbk'
        self.table = 'ii_sousi'

    def detail_handler(self, task, *args):
        data = super().detail_handler(task, *args)
        doc = data.get('doc')

        params = self.get_default_params(doc, data['url'])
        if not params['alias'] or params['alias'].isdigit():
            self.logger.warning('{}\t{}'.format(params['title'], task))
            return None

        action = params['alias']
        if r1('(VOL|NO)', params['title']):
            action = 'rosi'

        action = 'get_{}_params'.format(action)
        if hasattr(self, action):
            after_params = getattr(self, action)(params)
            params.update(after_params)

        self.save(params, i=args[0], n=args[1])

    def get_default_params(self, doc, url):
        origin_title = r2(r'\[.+?\]', doc(self.post_rule.get('title')).text())
        star = r1(r'((VOL|NO)\.\d+)\s([^[]+)', origin_title, 3, '')
        category = doc('.down_r_title a').eq(-1).text().replace('写真', '').replace('套图', '')
        category_en = r1(r'[a-zA-Z0-9]+', category, 0)
        if category_en and len(category_en) > 2 and category != category_en:
            category = category.replace(category_en, '')
        parse_result = parse.urlparse(url)
        alias = str(parse_result.path).replace('guochantaotu/', '').split('/')[1].lower()
        title = origin_title.replace(category, '')
        pwd, down_link = get_download_link_pwd(doc)
        status = 1 if down_link else 0
        return {
            'title': title, 'alias': alias,
            'star': star.replace('匿名寫真', '').replace('匿名写真', ''),
            'category': category,
            'download_link': down_link,
            'pwd': pwd,
            'url': url,
            'status': status,
            'number': ''
        }

    def get_rosi_params(self, params: dict):
        title = params['title']
        r = re.search(r'([a-zA-Z]+)\.(\d+)', title)
        number = 'no'
        if r:
            title = '{} {}'.format(params['category'], r.group(0))
            number = r.group(2)
        return {'title': title, 'number': number}


def get_download_link_pwd(doc):
    summary = doc('p.summary').text()
    pwd = ''
    if summary.find('资源无') != -1:
        pwd = ''
    elif summary.find('解压') != -1:
        re_pwd = re.search(r'【解压密码】([^\s]*)', summary)
        if re_pwd:
            pwd = re_pwd.group(1).strip()

    link_list = re.findall(r'[a-zA-z]+://[^\s]*', summary)
    if link_list and len(link_list):
        return pwd, _find_down_link(link_list)

    link_list = re.findall(r'[a-zA-z]+://[^\s]*', doc('#mbtxfont a').text())
    if link_list and len(link_list):
        return pwd, _find_down_link(link_list)
    return pwd, ''


def _find_down_link(link_list):
    for link in link_list:
        if re.search(r'file/[\d]+-[\d]+', link):
            return link

        if link.find('400gb') != -1 or link.find('ctfile') != -1 or link.find('474b') != -1 or link.find(
                't00y') != -1:
            return link
    return ''
