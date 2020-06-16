import re
from urllib import parse

from ..libs.base_handler import BaseHandler
from ..libs.common import r2, r1


class SouSi(BaseHandler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.sosi55.com'
        self.rule = {
            'page_url': '/guochantaotu/list_22_%page.html',
            'page_rule': {"list": '.yuanma_downlist_box .pic a'},
            'post_rule': {'title': '.single h1'},
            'base_url': self.base_url
        }
        self.charset = 'gbk'
        self.table = 'ii_sousi'

    def detail_handler(self, task, *args):
        data = super().detail_handler(task, *args)
        if not data or data.get('url').find('plus/') != -1:
            self.logger.error(task)
            return None

        doc = data.get('doc')
        try:
            params = self.get_default_params(doc, data['url'])
            if not params:
                return None

            if self.config.get('debug'):
                print(args[0], args[1], params)
            else:
                self.save(params, i=args[0], n=args[1])
        except Exception as e:
            self.logger.error(task)
            self.logger.exception(e)

    def get_default_params(self, doc, url):
        title = self.cc.convert(doc(self.post_rule.get('title')).text())
        _find = re.findall(r'\[[^\]]+\]', title)
        if len(_find) < 2:
            return None

        title = r2(r'\[[^\]]+\]|期|匿名写真|泰国旅拍合集|第二套|大理旅拍|第一刊|青春少女—|第四刊|越南芽庄|第三刊|三亚旅拍猩一|模特合集|动感之星|ShowTimeDancer', title)
        title = r2(r'\[[^\s]*|官网原图|原创写真|如壹写真|新模试镜|模特|（|）|上海|套图|一|二|三|原版|爱尤物专辑|高清重置|_|-|ROSI.CC|DISI.CC', title)
        title = r2(r'\.上|\.中|\.下|\+|经典001|MB|TuiGirl|第四印象', title)
        star = r1(r'MODEL(.*)|NO\.\d+(.*)|vol\.\d+(.*)', title, 1, '')
        print(star)
        if not star:
            star = title.split(' ')[-1]

        if star and star.find('：') != -1:
            star = star.split('：')[-1]

        alias = r1(r'[a-zA-Z0-9]+', _find[0], 0)
        category = r2(r'写真|\[|\]', _find[0])
        if category in ['XiuRen', '秀人网']:
            category = '秀人网'
            if not alias:
                alias = 'xiuren'

        if category in ['丽柜']:
            alias = 'ligui'

        if category != alias:
            category = r2(rf'{alias}', category)

        if title.find('美媛馆') != -1 or category.find('美媛馆') != -1:
            category = '美媛馆'
            alias = 'mygirl'
            title = r2('美媛馆', title)

        if not alias:
            parse_result = parse.urlparse(url)
            alias = str(parse_result.path).replace('guochantaotu/', '').split('/')[1].lower()

        pwd, down_link = get_download_link_pwd(doc)
        status = 1 if down_link else 0
        if category == alias:
            title = f'{category} {title}'
        elif alias:
            title = f'{alias.upper()}{category} {title}'

        title = r2('：', title, ' ')
        if star and star.find(' ') != -1:
            star = star.split(' ')[-1]

        return {
            'title': title.upper().strip(),
            'alias': alias.lower().strip(),
            'star': r2('套图|（二）|（一）|年费视频|黑网美腿|(一)|(二)|MODEL|车展|推女郎未流出版权图|第四印象|美缓馆', star, '', ''),
            'category': category,
            'download_link': down_link,
            'pwd': pwd,
            'url': url,
            'status': status,
            'number': r1(r'([a-zA-Z]+)\.(\d+)', title, 2, '')
        }


def get_download_link_pwd(doc):
    summary = doc('p.summary').text()
    pwd = ''
    if summary.find('资源无') != -1:
        pwd = ''
    elif summary.find('解压') != -1:
        re_pwd = re.search(r'【解压密码】([^\s]*)', summary)
        if re_pwd:
            pwd = re_pwd.group(1).strip().replace(':http', 'http')

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
                't00y') != -1 or link.find('bego.cc') != -1:
            return link
    return ''
