import requests


class BaseHttp:

    def __init__(self):
        self.http = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

    def fetch(self, url, data=None, method=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('headers', self.headers)

        if (data or kwargs.get('json')) and method is None:
            method = 'POST'

        if method is None:
            method = 'GET'

        response = self.http.request(method, url, data=data, **kwargs)
        if response.ok:
            return response
        raise Exception(response.status_code, response.request.url, response.text)
