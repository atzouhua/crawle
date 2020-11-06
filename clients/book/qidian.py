from clients.book import BaseBook


class QiDian(BaseBook):

    def __init__(self):
        super(QiDian, self).__init__()
        self.base_url = 'https://www.qidian.com'
        self.is_update = False
        self.rule = {
            'page_url': '/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=%page',
            'page_rule': {'list': '.all-book-list li a'},
            'post_rule': {},
            'base_url': 'https://www.qidian.com'
        }

    def action_index(self):
        url_list = self.get_page_url_list()
        n = len(url_list)
        if not n:
            self.logger.warning('empty url list.')
            return

        tasks = self.crawl(url_list, self.page_handler)
        print(tasks)
