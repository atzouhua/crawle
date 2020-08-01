import logging
import threading
import time

from .base_crawle import BaseCrawler
from .common import format_url, get_page_url_list
from .db import DB


class BaseClient(BaseCrawler):

    def __init__(self):
        super(BaseClient, self).__init__()
        self.config = {}
        self.rule = {}
        self.result = []
        self.tasks = []
        self.begin_tme = time.perf_counter()
        self.table = ''
        self.lock = threading.Lock()

    def action_before(self):
        self.rule.update(self.config)
        self.config = self.rule

    def action_after(self):
        if len(self.result):
            DB.insert_all(self.table, self.result)
            self.result = []
        self.process_time()

    def action_index(self):
        url_list = get_page_url_list(**self.config)
        n = len(url_list)
        if not n:
            self.logger.warning('empty url list.')
            return

        tasks = self.crawl(url_list, self.page_handler)
        task_count = len(tasks)
        self.logger.info(f'task count: {task_count}')
        if task_count:
            self.crawl(tasks, self.detail_handler)

    def action_detail(self):
        self.crawl([self.config.get('url')], self.detail_handler)

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

    def save(self, params, message=None, db_save=True, **kwargs):
        if not message:
            message = params['title']
        self.processing(kwargs.get('i'), kwargs.get('n'), message)
        if db_save:
            self.lock.acquire()
            self._db_save(params)
            self.lock.release()

    def _db_save(self, params: dict):
        self.result.append(params)
        if len(self.result) >= 50:
            DB.insert_all(self.table, self.result)
            self.result = []

    @property
    def post_rule(self):
        return self.config.get('post_rule')

    @property
    def page_rule(self):
        return self.config.get('page_rule')
