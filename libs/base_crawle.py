import logging
import time
from concurrent import futures

import pyquery
import requests
from requests.adapters import HTTPAdapter

from libs.request import Request

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
        self.config = {}

    def crawl(self, iterables, thread=None):
        result_list = []
        n = len(iterables)
        chunk_size = int(self.config.get('chunk_size')) or 1
        with futures.ThreadPoolExecutor(thread) as executor:
            try:
                args = ((item, (i + 1), n) for i, item in enumerate(iterables))
                for result in executor.map(lambda a: self.callback(*a), args, chunksize=chunk_size):
                    if result:
                        if type(result) == list:
                            result_list.extend(result)
                        else:
                            result_list.append(result)
            except Exception as e:
                self.logger.error(e)
        return result_list

    def callback(self, request: Request, index, total):
        try:
            request.doc = self.doc(request.url)
            request.index = index
            request.total = total
            return getattr(request, 'callback')(request)
        except Exception as e:
            self.logger.error(e)
            return None

    def fetch(self, url, data=None, method=None, **kwargs):
        kwargs.setdefault('timeout', 30)
        kwargs.setdefault('headers', self.headers)
        if data and method is None:
            method = 'POST'

        if method is None:
            method = 'GET'

        response = None
        for i in range(4):
            response = self.session.request(method, url, data=data, **kwargs)
            response.encoding = self.charset
            if response.ok:
                return response
            time.sleep(1)
        raise Exception(url, response.status_code, method)

    def doc(self, url, method='GET', **kwargs):
        if type(url) == dict:
            url = url.get('url')

        html = self.fetch(url, method=method, **kwargs).text
        return pyquery.PyQuery(html)
