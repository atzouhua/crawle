import json
import re
import time
from urllib.parse import urlparse

import requests


class CtFile:

    def __init__(self):
        self.base_url = 'https://ctfile.com/'
        self.request = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
        }

    def download(self, url):
        print('[+]: start downloading... %s' % url)
        url_info = urlparse(url)
        self.base_url = '{}://{}'.format(url_info.scheme, url_info.netloc)
        self.headers['Referer'] = url

        res = self.fetch(url)
        html = res.text
        try:
            title = re.search("<h3>([^<]*)<small>", html).group(1)
            uid = re.search("var userid = '(\d+)';", html).group(1)
            free_down = eval(re.search("free_down([^\"]*)", html).group(1))
            down_link = '%s/get_file_url.php?uid=%s&fid=%s&folder_id=0&file_chk=%s&mb=0&app=0&verifycode=&rd=%s' % (
                self.base_url, uid, free_down[0], free_down[2], '0.9708306371234965')
            return self._start_download(down_link, title)
        except Exception as e:
            print(e)
            return False

    def _start_download(self, down_link, title):
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        res = self.fetch(down_link, allow_redirects=False)
        data = json.loads(res.text)
        print(data)

        # wget_cmd = "wget -O %s '%s'" % (title, data['downurl'] + '&mtd=1')
        # print(wget_cmd)

        return True

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
    obj.download('https://sosi88.ctfile.com/fs/1801582-390307701')
