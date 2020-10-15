import logging
import threading
import time

from .base_crawle import BaseCrawler
from .common import format_url, DEV_ENV
from .config import Config


class BaseClient(BaseCrawler):

    def __init__(self):
        super(BaseClient, self).__init__()
        self.rule = {}
        self.result = []
        self.begin_tme = time.perf_counter()
        self.table = ''
        self.lock = threading.Lock()
        self.db = None
        self.dev_env = DEV_ENV
        self.publish_url = None

    def action_before(self):
        pass

    def action_after(self):
        self.process_time()

    def action_index(self):
        url_list = self.get_page_url_list()
        n = len(url_list)
        if not n:
            self.logger.warning('empty url list.')
            return

        tasks = self.crawl(url_list, self.page_handler)
        task_count = len(tasks)
        self.logger.info(f'task count: {task_count}')
        if task_count:
            self.crawl(tasks, self.detail_handler, chunk_size=Config.get('chunk_size'))

    def action_detail(self):
        detail_url: str = Config.get('detail_url')
        self.crawl(detail_url.split(','), self.detail_handler)

    def page_handler(self, task, *args):
        title_rule = self.page_rule.get('title')
        thumbnail_rule = self.page_rule.get('thumbnail')

        self.logger.info('[%s/%s] Get page: %s' % (args[0], args[1], task))
        doc = self.doc(task)
        elements = doc(self.page_rule.get('list'))
        result = []
        for element in elements.items():
            title = element.text()
            url = format_url(element.attr('href'), self.rule.get('base_url'))
            thumbnail = ''

            if title_rule:
                title = element(title_rule).text()
            if thumbnail_rule:
                thumbnail = element(thumbnail_rule).attr('src')
            data = {'title': title, 'url': url, 'thumbnail': thumbnail}
            result.append(data)
        return result

    def detail_handler(self, task, *args):
        if type(task) == dict:
            task = task.get('url')
        try:
            doc = self.doc(task)
            data = {}
            if self.post_rule:
                for field, rule in self.post_rule.items():
                    if field == 'thumbnail':
                        data[field] = doc(rule).attr('src')
                    else:
                        data[field] = doc(rule).text()
            data.setdefault('doc', doc)
            data.setdefault('url', task)
            return data
        except Exception as e:
            logging.error(e)
            return None

    def process_time(self):
        self.logger.info("process time {:.2f}s".format(time.perf_counter() - self.begin_tme))

    def processing(self, i, n, message):
        self.logger.info(f"[{i}/{n}]:{message}")

    def publish_api(self, data, *args):
        if Config.get('test'):
            self.logger.info(f"{args[0]}/{args[1]} {data['title']}")
            return data

        publish_url = Config.get('publish_url', self.publish_url)
        result = self.fetch(publish_url, data=data).json()
        self.logger.info(f"{args[0]}/{args[1]} {data['title']} {str(result)}")
        return result

    def save(self, params, message=None, db_save=False, **kwargs):
        if not message:
            message = params['title']
        self.processing(kwargs.get('i'), kwargs.get('n'), message)
        if db_save:
            self.lock.acquire()
            self._db_save(params)
            self.lock.release()

    def _db_save(self, params: dict):
        self.result.append(params)
        # if len(self.result) >= 50:
        #     DB.insert_all(self.table, self.result)
        #     self.result = []

    @property
    def post_rule(self):
        return self.rule.get('post_rule')

    @property
    def page_rule(self):
        return self.rule.get('page_rule')

    def get_page_url_list(self):
        tasks = []
        page_url = Config.get('page_url', self.rule.get('page_url'))
        start_page = Config.get('start_page', self.rule.get('start_page'))
        end_page = Config.get('end_page', self.rule.get('end_page'))

        if end_page < start_page:
            end_page = start_page

        for i in range(start_page, end_page + 1):
            url = page_url.replace('%page', str(i))
            tasks.append(format_url(url, self.rule.get('base_url')))

        tasks.reverse()
        return tasks
