import logging
import threading
import time
from concurrent import futures

import pyquery
import requests
from requests.adapters import HTTPAdapter

from .common import format_url, HTTP_PROXIES
from .db import DB

DEFAULT_POOL_SIZE = 50


class BaseHandler:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        self.proxies = HTTP_PROXIES
        self.session = requests.session()
        self.session.mount('https://',
                           HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_SIZE + 70))
        self.session.mount('http://',
                           HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_SIZE + 70))

        self.charset = 'utf-8'
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = {}
        self.rule = {}
        self.result = []
        self.tasks = []

        self.begin_tme = time.perf_counter()
        self.table = ''
        self.lock = threading.Lock()

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
        self.after_index(url_list)

    def after_index(self, url_list):
        tasks = self.crawl(url_list, self.page_handler)
        task_count = len(tasks)
        self.logger.info(f'task count: {task_count}')

        if task_count:
            self.crawl(tasks, self.detail_handler)

    def action_post(self):
        self.crawl([self.config.get('url')], self.detail_handler)

    def crawl(self, tasks: list, task_handler, thread_num=5, chunk_size=None):
        tasks.reverse()
        result_list = []
        n = len(tasks)
        thread_num = self.config.get('thread_num', thread_num)
        args = [i for i in range(1, n + 1)]
        args2 = [n for i in range(1, n + 1)]

        if not chunk_size:
            chunk_size = min(10, int(n / 5))
        with futures.ThreadPoolExecutor(thread_num) as executor:
            for num, result in zip(tasks, executor.map(task_handler, tasks, args, args2, chunksize=chunk_size)):
                if result:
                    if type(result) == list:
                        result_list.extend(result)
                    else:
                        result_list.append(result)
        return result_list

    def crawl2(self, tasks: list, fn, callback=None, **kwargs):
        tasks.reverse()
        n = len(tasks)
        thread_num = self.config.get('thread_num', kwargs.get('thread_num', 5))

        result_list = []
        with futures.ThreadPoolExecutor(thread_num) as executor:
            for i, task in enumerate(tasks):
                i += 1
                if type(task) == dict and task.get('url'):
                    kwargs.update(task)
                    task = task.get('url')
                try:
                    future = executor.submit(fn, task, i=i, n=n, **kwargs)
                    if callback:
                        future.add_done_callback(callback)
                    else:
                        result = future.result()
                        if result:
                            if type(result) == list:
                                result_list.extend(result)
                            elif type(result) == dict:
                                result_list.append(result)
                except Exception as e:
                    self.logger.exception(e)
        return result_list

    def get_html(self, url, method='GET', data=None, session=None, callback=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('proxies', self.proxies)
        kwargs.setdefault('headers', self.headers)
        if not session:
            session = self.session
        ex = None
        if data:
            method = 'POST'

        for i in range(3):
            try:
                response = session.request(method, url, data=data, **kwargs)
                response.encoding = self.charset
                if callback:
                    return response
                return response.text
            except Exception as e:
                ex = e
                time.sleep(1)
        raise ex

    def doc(self, url, method='GET', session=None, **kwargs):
        if type(url) == dict:
            url = url.get('url')
        return pyquery.PyQuery(self.get_html(url, method, session=session, **kwargs))

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
            logging.exception(e)

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
