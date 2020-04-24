import pyquery

from .base import BaseCrawler
from crawler.common import r1, r2


class SouSi(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.sosi55.com'
        self.rule = {
            'page_list_url': '/guochantaotu/list_22_%page.html',
            'end_page': 1,
            'start_page': 1,
            'page_rule': {"list": '.yuanma_downlist_box .pic a'},
            'post_rule': {"title": ".single h1"},
            'base_url': self.base_url
        }
        self.charset = 'gbk'
        self.category_map = {"ROSI": "rosi", "丽柜": "ligui", "动感小站": "dongganxiaozhan", "推女神": "tgod", "秀人网": "xiuren",
                             "嗲囡囡": "feilin", "V女郎": "vgirlmm", "DDY PANTYHOSE": "ddypantyhose", "尤果网": "ugirls",
                             "推女郎": "tuigirl", "波萝社": "bololi", "范模学院": "mfstar", "PANS": "pansidon",
                             "颜女神": "yannvshen", "美媛馆": "mygirl", "第四印象": "disi", "爱蜜社": "imiss", "爱丝": "aiss",
                             "果团网": "girlt", "魅妍社": "mistar", "模特联盟": "mtmeng", "3AGIRL": "3agirl", "51MODO": "51modo",
                             "蜜丝俱乐部": "missleg", "星颜社": "xingyan", "丝雅": "siyamm", "TPIMAGE": "tpimage", "影私荟": "wings",
                             "花漾": "huayang", "猫萌榜": "micat", "青豆客 ": "qingdouke", "糖果画报": "candy", "轰趴猫": "partycat",
                             "画语界": "xiaoyu", "尤物馆": "youwu", "御女郎": "dkgir", "尤蜜荟": "youmi", "顽味生活": "taste",
                             "蜜桃社": "miitao", "KIMOE": "kimoe", "星乐园": "leyuan", "优星馆": "uxing", "爱秀": "ishow",
                             "RU1MM": "ru1mm", "HEISIAI": "heisiai", "飞图网": "ftoow"}

    def _post_handler(self, task, **kwargs):
        data = super()._post_handler(task, **kwargs)
        doc = data.get('doc')
        content_elements = doc('#mbtxfont a')
        content = ''
        for element in content_elements.items():
            href = element.attr('href')
            if href.find('dbank') != -1 or href.find('vdisk') != -1 or href.find('guochantaotu') != -1:
                continue
            content = href
            break

        category = doc('.down_r_title a').eq(2).text().replace('写真', '').replace('套图', '')
        category, alias = self.get_title_category_alias(category)
        title = doc(self.post_rule.get('title')).text()
        title = r2(r'(\[.+?\])', title)
        title2 = r1(r'(VOL|NO)\.\d+', title, 0, title)
        star = r1(r'((VOL|NO)\.\d+)\s([^[]+)', title, 3)
        thumbnail = doc(self.post_rule.get('thumbnail'))
        print('[%s/%s]' % (kwargs.get('i'), kwargs.get('n')), title, [category, alias], [title2], [star])
        return [title, content, thumbnail]

    def get_title_category_alias(self, category: str):
        for k, v in self.category_map.items():
            if category.upper().find(k) != -1:
                return k, v
        return category, ''
