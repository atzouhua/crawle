from libs.base_client import BaseClient
from libs import r1


class SeHuaTang(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.sehuatang.net'
        self.rule = {
            'page_url': 'forum.php?mod=forumdisplay&fid=%cid&page=%page',
            'end_page': 1,
            'start_page': 1,
            'base_url': self.base_url,
            'page_rule': {'list': '#threadlisttableid tbody[id^="normalthread"] a.s'},
            'post_rule': {'title': '#thread_subject', 'magnet_link': '.blockcode li'},
        }
        self.table = 'ii_sehuatang'

    def action_test(self):
        print(self._get_image('dnjr-027'))

    def detail_handler(self, task, *args):
        data = super(SeHuaTang, self).detail_handler(task, *args)
        title = data['title']
        magnet_link = data['magnet_link']
        cid = int(self.config.get('cid'))
        status = 1 if magnet_link else 0
        params = {'url': data['url'], 'title': title, 'magnet_link': magnet_link, 'status': status, 'cid': cid}
        params.update(self.get_default_params(params, cid))
        self.save(params, i=args[0], n=args[1])

    def get_default_params(self, params, cid):
        if cid == 2 or cid == 104:
            return {}

        alias = r1(r'([a-zA-z0-9-]+-[0-9]+)', params['title'], 1, '')
        thumbnail = ''
        star = images = []
        if alias:
            thumbnail, images, star = self._get_image(alias)
            if len(images) > 10:
                images = images[0:10]
            alias = alias.upper()
        return {'alias': alias, 'star': star, 'thumbnail': thumbnail, 'images': images}

    def _get_image(self, alias):
        try:
            doc = self.doc('https://www.busdmm.one/{}'.format(alias))
            thumbnail = doc('.bigImage').attr('href')
            elements = doc('#sample-waterfall a')
            images = []
            for element in elements.items():
                images.append(element.attr('href'))
            star_elements = doc('.star-name a')
            star_list = []
            for element in star_elements.items():
                star_list.append(element.text())
            return thumbnail, images, star_list
        except Exception as e:
            self.logger.debug(e)
            doc = self.doc('http://www.jav321.com/search', {'sn': alias})
            elements = doc('.row .col-md-3 .col-xs-12 a img')
            images = []
            for element in elements.items():
                images.append(element.attr('src'))
            if images:
                return images[0], images[1:], []
            return '', [], []
