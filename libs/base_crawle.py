import logging
import os
from concurrent import futures

import pyquery
import requests
from requests.adapters import HTTPAdapter

DEFAULT_POOL_SIZE = 100
HTTP_ADAPTER = HTTPAdapter(pool_connections=DEFAULT_POOL_SIZE, pool_maxsize=DEFAULT_POOL_SIZE + 300)


class BaseCrawler:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
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
            chunk_size = min(5, chunk_size)

        with futures.ThreadPoolExecutor(thread_num) as executor:
            try:
                args = ((item, i + 1, n) for i, item in enumerate(tasks))
                for result in executor.map(lambda a: task_handler(*a), args, chunksize=chunk_size):
                    if result:
                        if type(result) == list:
                            result_list.extend(result)
                        else:
                            result_list.append(result)
            except Exception as e:
                self.logger.error(e)
        return result_list

    def fetch(self, url, data=None, method=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('headers', self.headers)
        if data and method is None:
            method = 'POST'

        if method is None:
            method = 'GET'

        response = self.session.request(method, url, data=data, **kwargs)
        response.encoding = self.charset
        if not response.ok:
            raise Exception(url, response.status_code, method)
        return response

    def doc(self, url, method='GET', **kwargs):
        return self.document(url, method, **kwargs)

    def document(self, url, method='GET', **kwargs):
        if type(url) == dict:
            url = url.get('url')

        html = self.fetch(url, method=method, **kwargs).text
        return pyquery.PyQuery(html)
