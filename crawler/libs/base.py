import logging
import os
import time
from concurrent import futures

import pyquery
import requests
from requests.adapters import HTTPAdapter

from .common import format_url, HTTP_PROXIES
from .db import DB

DEFAULT_POOL_SIZE = 20


class BaseHandler:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        self.proxies = HTTP_PROXIES
        self.session = requests.session()
        self.session.mount('https://', HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_SIZE))
        self.session.mount('http://', HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_SIZE))

        self.charset = 'utf-8'
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = {}
        self.rule = {}
        self.result = []
        self.tasks = []

        self.begin_tme = time.perf_counter()
        self.table = ''

    def before_run(self):
        pass

    def after_run(self):
        if len(self.result):
            DB.insert_all(self.table, self.result)
            self.result = []
        self.process_time()

    def run(self):
        _action = 'action_{}'.format(self.config.get('action', 'index'))
        if hasattr(self, _action):
            func = getattr(self, _action)
            func()

    def action_index(self):
        url_list = self.get_index_url_list()
        n = len(url_list)
        if not n:
            self.logger.warning('empty url list.')
            return

        tasks = self.crawl(url_list, self.page_handler)
        task_count = len(tasks)
        self.logger.info(f'task count: {task_count}')

        if task_count:
            self.crawl(tasks, self.detail_handler)

    def crawl(self, tasks: list, task_handler=None):
        tasks.reverse()
        result_list = []
        n = len(tasks)
        thread_num = self.config.get('thread_num', 20)
        args = [i for i in range(1, n + 1)]
        args2 = [n for i in range(1, n + 1)]

        chunk_size = min(20, int(n / 5))
        chunk_size = max(30, chunk_size)
        with futures.ThreadPoolExecutor(thread_num) as executor:
            for num, result in zip(tasks, executor.map(task_handler, tasks, args, args2, chunksize=chunk_size)):
                if result:
                    if type(result) == list:
                        result_list.extend(result)
                    else:
                        result_list.append(result)
        return result_list

    def get_html(self, url, method='GET', callback=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('proxies', self.proxies)
        kwargs.setdefault('headers', self.headers)
        # kwargs.setdefault('verify', False)
        ex = None

        for i in range(3):
            try:
                response = self.session.request(method, url, **kwargs)
                response.encoding = self.charset
                if callback:
                    return callback(response)
                return response.text
            except Exception as e:
                ex = e
                time.sleep(1)
        raise ex

    def doc(self, url, method='GET', **kwargs):
        if type(url) == dict:
            url = url.get('url')
        return pyquery.PyQuery(self.get_html(url, method, None, **kwargs))

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
            return data
        except Exception as e:
            logging.exception(e)

    def process_time(self):
        self.logger.info("process time {:.2f}s".format(time.perf_counter() - self.begin_tme))

    def processing(self, i, n, message):
        self.logger.info(f"[{i}/{n}]:{message}")

    def on_result(self, future):
        result = future.result()
        result_info = result[1]
        self.processing(result_info['i'], result_info['n'], result[0]['title'])

    def save(self, params, message, db_save=True, **kwargs):
        self.processing(kwargs.get('i'), kwargs.get('n'), message)
        if db_save:
            self._db_save(params)

    def _db_save(self, params: dict):
        self.result.append(params)
        if len(self.result) >= 50:
            DB.insert_all(self.table, self.result)
            self.result = []

    @property
    def post_rule(self):
        return self.rule.get('post_rule')

    @property
    def page_rule(self):
        return self.rule.get('page_rule')

    def get_index_url_list(self):
        tasks = []
        page_url = self.config.get('url')
        base_url = self.rule.get('base_url')
        if not page_url:
            page_url = self.rule.get('page_url')
            if self.rule.get('append_page_url'):
                tasks.append(format_url(self.rule.get('append_page_url'), base_url))

        start_page = self.config.get('start', self.rule.get('start_page', 1))
        end_page = self.config.get('end', self.rule.get('end_page', 1))

        if end_page < start_page:
            end_page = start_page + 1

        for i in range(start_page, end_page + 1):
            url = page_url.replace('%page', str(i))
            if url.find('%cid') != -1:
                url = url.replace('%cid', str(self.config.get('cid')))
            tasks.append(format_url(url, base_url))

        tasks.reverse()
        return tasks
