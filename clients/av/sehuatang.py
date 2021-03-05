import re

from libs.base_client import BaseClient
from libs.common import md5


class SeHuaTang(BaseClient):

    def __init__(self):
        super().__init__()
        self.rule = {
            'start_url': 'forum.php?mod=forumdisplay&fid=103&page=%page',
            'base_url': 'https://www.sehuatang.net',
            'page_rule': {'list': '#threadlisttableid tbody[id^="normalthread"] a.s'},
        }
        self.col = None

    def before_run(self):
        db = self.get_db()
        self.col = db.get_collection('sehuatang')

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

        _id = md5(alias)
        data = {'alias': alias, 'magnet_link': magnet_link, '_id': _id}
        try:
            self.col.insert_one(data)
        except Exception as e:
            self.logger.error(e)
        return data
