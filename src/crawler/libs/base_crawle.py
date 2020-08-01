import logging
import os
import time
from concurrent import futures

import pyquery
import requests
from requests.adapters import HTTPAdapter

DEFAULT_POOL_SIZE = 50
HTTP_ADAPTER = HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_SIZE + 70)


class BaseCrawler:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        self.session = requests.session()
        self.session.mount('https://', HTTP_ADAPTER)
        self.session.mount('http://', HTTP_ADAPTER)

        self.charset = 'utf-8'
        self.logger = logging.getLogger(self.__class__.__name__)

    def crawl(self, tasks: list, task_handler, thread_num=5, chunk_size=None):
        tasks.reverse()
        result_list = []
        n = len(tasks)
        if not chunk_size:
            chunk_size, extra = divmod(n, (os.cpu_count() or 1) * 4)

        with futures.ThreadPoolExecutor(thread_num) as executor:
            try:
                args = ((item, i, n) for i, item in enumerate(tasks))
                for result in executor.map(lambda a: task_handler(*a), args, chunksize=chunk_size):
                    if result:
                        if type(result) == list:
                            result_list.extend(result)
                        else:
                            result_list.append(result)
            except Exception as e:
                self.logger.error(e)
        return result_list

    def get_html(self, url, method='GET', data=None, **kwargs):
        response = None
        ex = None
        for i in range(3):
            try:
                response = self.fetch(url, data=data, method=method, **kwargs)
                if response.ok:
                    return response.text
            except Exception as e:
                ex = e
                time.sleep(2)
        raise Exception(url, response.status_code)

    def fetch(self, url, data=None, method=None, session=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('headers', self.headers)
        if data and method is None:
            method = 'POST'

        if method is None:
            method = 'GET'

        if session is None:
            session = self.session

        response = session.request(method, url, data=data, **kwargs)
        response.encoding = self.charset
        return response

    def doc(self, url, method='GET', session=None, **kwargs):
        if type(url) == dict:
            url = url.get('url')
        return pyquery.PyQuery(self.get_html(url, method, session=session, **kwargs))
