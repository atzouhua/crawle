import base64
import json
import os
import re

import requests

from crawler.utils.http import HttpClient


class WeiBo:

    def __init__(self):
        self.user = 'jblog110@gmail.com'
        self.pwd = 'hack3321'
        self.http = HttpClient()
        self.cookie_file = 'wb.cookie'

    def login(self):
        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)&_=1403138799543'
        su = base64.b64encode(self.user.encode('utf-8'))
        params = {'entry': 'sso', 'gateway': 1, 'from': 'null', 'savestate': 30, 'useticket': 0, 'pagerefer': '',
                  'vsnf': 1, 'su': su, 'service': 'sso', 'sp': self.pwd, 'sr': '1920*1080', 'encoding': 'UTF-8',
                  'cdult': 3, 'domain': 'sina.com.cn', 'prelt': 0, 'returntype': 'TEXT'}
        res = self.http.fetch(login_url, params)
        cookies_dict = requests.utils.dict_from_cookiejar(res.cookies)
        with open(self.cookie_file, 'w') as f:
            f.write(json.dumps(cookies_dict))

    def upload(self, file):
        b64_data = self.get_file_data(file)
        return self.upload_base64(b64_data)

    def upload_base64(self, b64_data):
        if not os.path.isfile(self.cookie_file):
            self.login()

        with open(self.cookie_file, 'r') as f:
            data = f.read()

        cookies = json.loads(data)
        upload_url = 'http://picupload.service.weibo.com/interface/pic_upload.php?mime=image%2Fjpeg&data=base64&url=0&markpos=1&logo=&nick=0&marks=1&app=miniblog'
        params = {'b64_data': b64_data}
        res = self.http.fetch(upload_url, params, cookies=cookies)
        res = re.search('({.+)', res.text)
        if not res:
            return None

        data = json.loads(res.group(1))
        if data['code'] != 'A00006':
            self.login()
            return self.upload_base64(b64_data)

        image_id = data.get('data').get('pics').get('pic_1').get('pid')
        return 'http://ww3.sinaimg.cn/large/%s' % image_id

    def get_file_data(self, file):
        with open(file, 'rb') as f:
            base64_data = base64.b64encode(f.read())
        return base64_data
