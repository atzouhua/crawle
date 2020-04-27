import json
import os
import random
import re
import time

import pyquery
from requests.cookies import cookiejar_from_dict
from requests.utils import dict_from_cookiejar

from crawler.common import DATA_PATH, SS_PROXIES
from .base import BaseCrawler


class T66y(BaseCrawler):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://t66y.com'
        self.page_url = 'thread0806.php?fid=7&search=today'
        self.charset = 'gbk'
        self.proxies = SS_PROXIES
        self.user = 'lewei123'
        self.pwd = 'hack3321'
        self.cookie_file = ''

    def before_run(self):
        super(T66y, self).before_run()
        self.http.headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3239.108 Safari/537.36'
        self.cookie_file = os.path.join(DATA_PATH, 't66y_{}.cookie'.format(self.user))

    def run(self):
        self.load_cookies()
        profile = self.get_profile()
        if not profile or profile.find(self.user) == -1:
            self.login()
            profile = self.get_profile()

        if not profile or profile.find(self.user) == -1:
            raise Exception('[{}] login error.'.format(self.user))

        self.logger.info(profile)

        if profile.find('俠客') != -1:
            return

        n = random.randint(6, 11)
        i = 0
        while True:
            self.reply()
            second = random.randint(1024, 1124)
            self.logger.info('time wait: {}s'.format(second))
            time.sleep(second)
            i += 1
            if i > n:
                break

    def reply(self, content='1024'):
        data = self.get_reply_post()
        re_title = 'Re:%s' % data['title']
        params = {'atc_autourl': '1', 'atc_usesign': '1', 'atc_convert': '1',
                  'atc_content': content.encode(self.charset, errors='ignore'),
                  'atc_title': re_title.encode(self.charset, errors='ignore'),
                  'tid': data['tid'],
                  'fid': '7',
                  'step': '2', 'action': 'reply', 'pid': '', 'verify': 'verify'
                  }
        html = self.http.html('%s/post.php?' % self.base_url, data=params)
        if html.find('發貼完畢點擊進入主題列表') != -1:
            self.logger.info('【%s】reply success!' % data['title'])
            return True
        if html.find('在1024秒內不能發貼') != -1:
            self.logger.info('1024秒內不能發貼')
            return False
        if html.find('用戶組權限') != -1:
            self.logger.info('用戶組權限：你所屬的用戶組每日最多能發 10 篇帖子')
            return False

        self.logger.info('【%s】reply fail!' % data['title'])

        try:
            doc = pyquery.PyQuery(html)
            element = doc('#main div.t').eq(0)
            message = element('center').text()
            if message:
                self.logger.info(message)
        except Exception as e:
            self.logger.exception(e)
        return False

    def get_reply_post(self):
        pending_post_list = []
        tid_list = self.get_my_reply_list()

        url = '%s/%s' % (self.base_url, self.page_url)
        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        elements = doc('#ajaxtable .tr3')
        for element in elements.items():
            element_a = element('td').eq(1)
            element_a = element_a('a')
            post_url = element_a.attr('href')
            title = element_a.text()
            if title.find('求片求助貼') != -1 or post_url.find('htm_data') == -1:
                continue

            reply_num = int(element('td').eq(3).text())
            if reply_num < 25 or reply_num > 300:
                continue

            # print(reply_num, post_url, title)

            tid_re = re.search('/([0-9]+)\\.html', post_url)
            if not tid_re:
                continue

            tid = tid_re.group(1)
            if tid_list and tid_list.find(tid) != -1:
                continue

            pending_post_list.append({'title': title, 'tid': tid})

        if len(pending_post_list) > 0:
            return random.choice(pending_post_list)

        raise Exception('Not found post.')

    def get_my_reply_list(self):
        url = '%s/personal.php?action=post' % self.base_url
        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        elements = doc('.t3 div.t .a2')
        tid_list = []
        for element in elements.items():
            href = element.attr('href')
            tid = re.search('tid=([0-9]+)&', href).group(1)
            tid_list.append(tid)
        return ' '.join(tid_list)

    def get_profile(self):
        url = '%s/profile.php' % self.base_url
        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        element = doc('#main .t3').eq(1)
        element = element('table td').eq(0)
        element = element('div.t').eq(1)
        info = element.text()
        return re.sub(r'\s', ' ', info)

    def login(self):
        self.logger.info('[{}] Start login.'.format(self.user))
        url = self.base_url + '/login.php'
        jump_url = '%s/%s' % (self.base_url, self.page_url)
        params = {'jumpurl': jump_url, 'pwuser': self.user, 'pwpwd': self.pwd, 'forward': jump_url, 'step': 2,
                  'cktime': 86400 * 365}
        res = self.http.fetch(url, params)
        res.encoding = self.charset
        html = res.text
        if html.find('您已經順利登錄') != -1:
            self.logger.info('[{}] login success'.format(self.user))
            self.save_cookies(res.cookies)
            return

        if html.find('您登录尝试次数过多') != -1:
            raise Exception('您登录尝试次数过多，需要输入验证码才能继续')

        raise Exception('login fail')

    def load_cookies(self):
        if os.path.exists(self.cookie_file) and os.path.getsize(self.cookie_file) > 10:
            with open(self.cookie_file, 'r') as f:
                cookies = f.read()
            cookies = cookiejar_from_dict(json.loads(cookies))
            self.http.request.cookies = cookies
        else:
            self.login()

    def save_cookies(self, cookies):
        with open(self.cookie_file, 'w') as f:
            f.write(json.dumps(dict_from_cookiejar(cookies)))
