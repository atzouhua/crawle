import re

from libs.base_client import BaseClient


class SeHuaTang(BaseClient):

    def __init__(self):
        super().__init__()
        self.rule = {
            'start_url': 'forum.php?mod=forumdisplay&fid=103&page=%page',
            'base_url': 'https://www.sehuatang.net',
            'page_rule': {'list': '#threadlisttableid tbody[id^="normalthread"] a.s'},
        }

    def parse_page(self, response):
        doc = response.doc

        alias = doc('#thread_subject').text()
        r = re.search(r'([A-Z]+-[0-9]+)', alias)
        if not r:
            return None

        alias = r.group(1)

        self.logger.info(f"{response.index}/{response.total}: {alias}.")

        magnet_link = doc('.blockcode li').text().strip()
        if not magnet_link:
            return None

        return {'alias': alias, 'magnet_link': magnet_link}

    def save(self, data):
        self.do_save(data, 'sehuatang_mgstage', 'alias')
