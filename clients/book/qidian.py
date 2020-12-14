from clients.book import BaseBook


class QiDian(BaseBook):

    def __init__(self):
        super(QiDian, self).__init__()
        self.base_url = 'https://www.qidian.com'
        self.is_update = False
        self.rule = {
            'page_url': '/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=%page',
            'page_rule': {'list': '.all-book-list li .book-mid-info h4 a'},
            'post_rule': {},
            'base_url': 'https://www.qidian.com'
        }

    def detail_handler(self, task, *args):
        data = super().detail_handler(task, *args)
        if not data:
            self.logger.error(task)
            return None

        doc = data.get('doc')
        title = doc('.book-info h1 em').text()
        description = doc('.book-intro').text()
        thumbnail = doc('.book-img img').attr('src')
        book_items = doc('.volume .cf li')

        self.logger.info(f'{title} {len(book_items)} {self.session.cookies}')

