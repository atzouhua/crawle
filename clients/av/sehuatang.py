from libs.base_client import BaseClient


class SeHuaTang(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.sehuatang.net'
        self.rule = {
            'start_url': 'forum.php?mod=forumdisplay&fid=104&page=%page',
            'base_url': self.base_url,
            'page_rule': {'list': '#threadlisttableid tbody[id^="normalthread"] a.s'},
        }

    def parse_page(self, response):
        doc = response.doc
        alias = doc('#thread_subject').text().split(' ')[0].strip()

        self.logger.info(f"{response.index}/{response.total}: {alias}.")

        magnet_link = doc('.blockcode li').text().strip()
        if not magnet_link:
            return None

        return {'alias': alias, 'magnet_link': magnet_link}
