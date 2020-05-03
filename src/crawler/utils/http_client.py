import time

import requests

from .log import Logging
from .ua import FakerUa


class HttpClient:
    os_type = [
        '(Windows NT 6.1; WOW64)',
        '(Windows NT 10.0; WOW64)',
        '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)',
        '(Macintosh; Intel Mac OS X 10_13)',
    ]

    def __init__(self):
        self.request = requests.session()
        self.headers = {
            'User-Agent': FakerUa.get_ua()
        }
        self.proxies = None
        self.logger = Logging.get(__name__)
        self.error = None
        self.charset = 'utf-8'

    def fetch(self, url, data=None, **kwargs):
        response = None

        self.headers['Referer'] = url
        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('timeout', 20)
        kwargs.setdefault('proxies', self.proxies)
        for i in range(1, 4):
            try:
                if data is None:
                    response = self.request.get(url, **kwargs)
                else:
                    response = self.request.post(url, data, **kwargs)

                if response.ok:
                    return response

                self.error = response.status_code, response.text
            except Exception as e:
                time.sleep(1)
                self.error = e
                self.logger.warning('retry [%s] %s %s' % (i, url, e))
                continue

        if not response:
            raise Exception(self.error, url)

        return response

    def ajax(self, url, data=None, **kwargs):
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        return self.fetch(url, data, **kwargs)

    def html(self, url, data=None, **kwargs):
        response = self.fetch(url, data, **kwargs)
        response.encoding = kwargs.get('charset', self.charset)
        return response.text
