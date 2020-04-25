from urllib import parse

import pyquery

from .base import BaseCrawler
from crawler.common import r1, r2

category_alias_map = {"ROSI": "rosi", "丽柜": "ligui", "推女神": "tgod", "秀人网": "xiuren",
                      "嗲囡囡": "feilin", "V女郎": "vgirlmm", "DDY PANTYHOSE": "ddypantyhose", "尤果网": "ugirls",
                      "推女郎": "tuigirl", "波萝社": "bololi", "范模学院": "mfstar",
                      "颜女神": "yannvshen", "美媛馆": "mygirl", "第四印象": "disi", "爱蜜社": "imiss", "爱丝": "aiss",
                      "果团网": "girlt", "魅妍社": "mistar", "模特联盟": "mtmeng", "3AGIRL": "3agirl", "51MODO": "51modo",
                      "蜜丝俱乐部": "missleg", "星颜社": "xingyan", "丝雅": "siyamm", "影私荟": "wings",
                      "花漾": "huayang", "猫萌榜": "micat", "青豆客 ": "qingdouke", "糖果画报": "candy", "轰趴猫": "partycat",
                      "画语界": "xiaoyu", "尤物馆": "youwu", "御女郎": "dkgir", "尤蜜荟": "youmi", "顽味生活": "taste",
                      "蜜桃社": "miitao", 'MiiTao蜜桃社': 'miitao', "KIMOE": "kimoe", "星乐园": "leyuan", "优星馆": "uxing",
                      "爱秀": "ishow",
                      "RU1MM": "ru1mm", "HEISIAI": "heisiai", "飞图网": "ftoow", 'YouWu尤物馆': 'youwu'}


class SouSi(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.sosi55.com'
        self.rule = {
            'page_list_url': '/guochantaotu/list_22_%page.html',
            'end_page': 50,
            'start_page': 1,
            'page_rule': {"list": '.yuanma_downlist_box .pic a'},
            'post_rule': {"title": ".single h1"},
            'base_url': self.base_url
        }
        self.charset = 'gbk'

        parse_result = parse.urlparse('/guochantaotu/ROSI/2011/0531/5577.html')
        url = str(parse_result.path)
        exit()

    def _post_handler(self, task, **kwargs):
        data = super()._post_handler(task, **kwargs)
        doc = data.get('doc')

        params = self.get_default_params(doc, data['url'])
        if not params['alias']:
            self.logger.error('not found alias. {}, {}'.format(params['title'], task))
            return

        alias = params['alias']
        action_map = {'rosi': 'rosi', 'xiuren': 'rosi', 'miitao': 'rosi', 'xiaoyu': 'rosi', 'youwu': 'rosi',
                      'mfstar': 'rosi', 'youmi': 'rosi', 'xingyan': 'rosi', 'imiss': 'rosi', 'huayang': 'rosi',
                      'mygirl': 'rosi', 'mfstar': 'rosi', 'ugirls': 'rosi'}
        action = action_map.get(alias) if action_map.get(alias) else alias
        action = 'get_{}_params'.format(action)
        if hasattr(self, action):
            after_params = getattr(self, action)(params)
            params.update(after_params)
        print(params)

    def get_default_params(self, doc, url):
        origin_title = r2(r'(\[.+?\])', doc(self.post_rule.get('title')).text())
        star = r1(r'((VOL|NO)\.\d+)\s([^[]+)', origin_title, 3, '')
        category = doc('.down_r_title a').eq(-1).text().replace('写真', '')
        category = category.replace('套图', '').replace('MiiTao蜜桃社', '蜜桃社').replace('YouWu尤物馆', '尤物馆')
        alias = str(url.split('/')[-4]).lower()
        title = origin_title.replace(category, '')
        return {
            'title': title, 'alias': alias,
            'star': star, 'category': category,
            'download_link': get_download_link(doc),
            'url': url
        }

    def get_rosi_params(self, params: dict):
        number = r1(r'(Vol|NO)\.\d+', params['title'], 0)
        title = '{} {}'.format(params['category'], number)
        return {'title': title}


def get_alias(url):
    data = url.split('/')

def get_download_link(doc):
    content_elements = doc('#mbtxfont a')
    for element in content_elements.items():
        href = element.attr('href')
        if href.find('dbank') != -1 or href.find('vdisk') != -1 or href.find('guochantaotu') != -1 or href.find(
                '115') != -1:
            continue
        return href
    return ''
