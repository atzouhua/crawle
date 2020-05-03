import json
import random
import re
import time
from urllib.parse import urlparse

import requests


class CtFile:

    def __init__(self):
        self.base_url = 'https://474b.com'
        self.request = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
        }
        self.download_api = 'https://webapi.ctfile.com/get_file_url.php?uid={}&fid={}&folder_id=0&file_chk={}&mb=0&app=0&acheck=1&verifycode=&rd={}'

    def download(self, url):
        url = 'http://www.400gb.com/file/80638823'
        url = url.replace('http:', 'https:')
        print('[+]: start downloading... %s' % url)
        response = self.fetch(url, allow_redirects=False)
        if response.status_code == 302:
            url = response.headers['location']
        file_id = url.split('/')[-1]
        self.headers['Referer'] = url
        self.headers['Origin'] = 'https://545c.com'
        api = 'https://webapi.ctfile.com/getfile.php?f={}&passcode=&r={}&ref='.format(file_id, random.random())
        response = self.fetch(api)
        data = json.loads(response.text)
        title = data['file_name']

        download_api = self.download_api.format(data['userid'], data['file_id'], data['file_chk'], random.random())
        response = self.fetch(download_api)
        data = json.loads(response.text)
        wget_cmd = "wget -O %s '%s'" % (title, data['downurl'])
        print(wget_cmd)

        data = {
            'append': 'list-home',
            'paged': 1000,
            'action': 'ajax_load_posts',
            'page': 'home'
        }
        response = self.fetch('https://www.vmgirls.com/wp-admin/admin-ajax.php', data=data)
        print(response.text)

    def fetch(self, url, data=None, **kwargs):
        response = None

        kwargs.setdefault('headers', self.headers)
        kwargs.setdefault('timeout', 20)
        # kwargs.setdefault('proxies', PROXIES)

        for i in range(3):
            try:
                if data is None:
                    response = self.request.get(url, **kwargs)
                else:
                    response = self.request.post(url, data, **kwargs)
                if response.ok:
                    return response
            except Exception as e:
                time.sleep(1)
                print('retry [%s] %s %s' % (i, url, e))
                continue
        return response


if __name__ == '__main__':
    obj = CtFile()
    obj.download('https://474b.com/file/1801582-440521095')
