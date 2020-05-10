import re

import pyquery

from src.crawler.extractors import BaseProvider


class Meitulu(BaseProvider):

    def __init__(self):
        BaseProvider.__init__(self)
        self.base_url = 'https://www.meitulu.com'
        self.page_list_url = '/t/xiuren/%page.html'
        # self.append_page_list_url = '%s/t/xiuren' % self.base_url
        self.start_page = 2
        self.proxies = None
        self.rule = {
            'page_rule': {
                "list": ".main ul.img li",
                "url": " .p_title a",
            },
            'post_rule': {
                "title": ".weizhi h1",
            }
        }

    def _parse_post(self, task, **kwargs):
        post_rule = self.rule.get('post_rule')
        title_rule = post_rule.get('title')
        if type(task) == dict and task.get('url'):
            task = task.get('url')

        html = self.get_html(task)
        doc = pyquery.PyQuery(html)
        title = doc(title_rule).text()
        title = re.sub('\\[[0-9a-zA-Z+.]+\\]|写真', '', title)
        re_num = re.search('图片数量： ([0-9]+) 张', html)
        num = int(re_num.group(1))
        tag = doc('.c_l p').eq(4).text()

        content = []
        for i in range(1, num + 1):
            content.append('https://mtl.ttsqgs.com/images/img/18514/{}.jpg'.format(i))

        print('[%s/%s]' % (kwargs.get('i'), kwargs.get('n')), title, content, tag, task)
        return [title, content, tag]
