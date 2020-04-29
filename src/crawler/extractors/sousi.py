import re
from urllib import parse

from crawler.common import r1, r2
from .base import BaseCrawler
from ..utils.config import Config


class SouSi(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.sosi55.com'
        self.rule = {
            'page_list_url': '/guochantaotu/list_22_%page.html',
            'end_page': 1500,
            'start_page': 1500,
            'page_rule': {"list": '.yuanma_downlist_box .pic a'},
            'post_rule': {"title": ".single h1"},
            'base_url': self.base_url
        }
        self.charset = 'gbk'
        self.table = 'sousi'

    def _post_handler(self, task, **kwargs):
        data = super()._post_handler(task, **kwargs)
        doc = data.get('doc')

        params = self.get_default_params(doc, data['url'])
        if not params['alias'] or params['alias'].isdigit():
            self.logger.error('not found alias. {}, {}'.format(params['title'], task))
            return

        action = params['alias']
        if r1('(VOL|NO)', params['title']):
            action = 'rosi'

        action = 'get_{}_params'.format(action)
        if hasattr(self, action):
            after_params = getattr(self, action)(params)
            params.update(after_params)

        if not params['download_link']:
            params['status'] = 0

        self.save(params, **kwargs)

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
        return {
            'title': title, 'alias': alias,
            'star': star.replace('匿名寫真', ''),
            'category': category,
            'download_link': down_link,
            'pwd': pwd,
            'url': url,
            'status': 1
        }

    def get_rosi_params(self, params: dict):
        title = params['title']
        number = r1(r'(Vol|NO)\.\d+', title, 0)
        if number:
            title = '{} {}'.format(params['category'], number)
        return {'title': title}


def get_download_link_pwd(doc):
    summary = doc('p.summary').text()
    pwd = ''
    if summary.find('资源无密码') != -1:
        pwd = ''
    elif summary.find('解压') != -1:
        re_pwd = re.search(r'【解压密码】([^\s]*)', summary)
        if re_pwd:
            pwd = re_pwd.group(1).strip()
        else:
            print(summary)

    link_list = re.findall(r'[a-zA-z]+://[^\s]*', summary)
    if link_list and len(link_list):
        return pwd, _find_down_link(link_list)

    link_list = re.findall(r'[a-zA-z]+://[^\s]*', doc('#mbtxfont a').text())
    if link_list and len(link_list):
        return pwd, _find_down_link(link_list)

    # content_elements = doc('#mbtxfont a')
    # for element in content_elements.items():
    #     href = element.attr('href')
    #     if href.find('400gb') != -1 or href.find('ctfile') != -1 or href.find('474b') != -1 or href.find('t00y') != -1:
    #         return href
    return pwd, ''


def _find_down_link(link_list):
    for link in link_list:
        if link.find('400gb') != -1 or link.find('ctfile') != -1 or link.find('474b') != -1 or link.find(
                't00y') != -1:
            return link
    return ''
