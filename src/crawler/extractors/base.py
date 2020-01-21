import threading
import time
import unicodedata
from concurrent import futures

import pyquery
from progress.bar import Bar

from crawler.utils.http import HttpClient
from crawler.utils.log import Logging
from crawler.utils.common import format_url, get_progress_bar, get_tasks
from crawler.utils.config import Config
from crawler.utils.exceptions import HttpException


class BaseCrawler:

    def __init__(self):
        self.lock = threading.Lock()
        self.thread_num = 10

        self.publish_api = 'http://hahamh.net/api/post-save'

        self.rule = {}
        self.bar = None
        self.data = []

        self.logger = Logging.getLogger()
        self.proxies = None
        self.charset = 'utf-8'
        self.http = HttpClient()
        self.begin_tme = time.time()
        self.name = self.__class__.__name__
        self.post_handler = self._post_handler
        self.post_callback = None

    def before_run(self):
        self.http.charset = self.charset
        self.http.proxies = self.proxies

    def after_run(self):
        pass

    def run(self):
        action = 'action_%s' % Config.get('action', 'index')
        if hasattr(self, action):
            func = getattr(self, action)
            func()

    def action_index(self):
        index_tasks = get_tasks(self.rule)
        n = len(index_tasks)
        if not n:
            self.logger.info('empty tasks.')
            return

        thread_num = min(n, 5)
        result = self.execute(index_tasks, self._index_handler, thread_num=thread_num)

        n = len(result)
        self.logger.info('Get task done. tasks count: %s' % n)

        thread_num = min(n, Config.get('thread', self.thread_num))
        self.bar = get_progress_bar(n)
        self.execute(result, fn=self.post_handler, callback=self.post_callback, thread_num=thread_num,
                     bar=Bar(max=1))
        self.bar.finish()

    def action_post(self):
        post_url = Config.get('url')
        return self._post_handler(post_url, i=1, n=1)

    def _index_handler(self, url: str, **kwargs) -> list:
        page_rule = self.rule.get('page_rule')
        title_rule = page_rule.get('title')
        url_rule = page_rule.get('url')
        thumbnail_rule = page_rule.get('thumbnail')

        self.logger.info('[%s/%s] Get page: %s' % (kwargs.get('i'), kwargs.get('n'), url))
        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        elements = doc(page_rule.get('list'))
        result = []
        for element in elements.items():
            element_a = element(url_rule)
            title = element_a.text()
            url = format_url(element_a.attr('href'), self.rule.get('base_url'))
            thumbnail = ''

            if title_rule:
                title = element(title_rule).text()
            if thumbnail_rule:
                thumbnail = element(thumbnail_rule).attr('src')
            result.append({'title': title, 'url': url, 'thumbnail': thumbnail})
        return result

    def _post_handler(self, url, **kwargs):
        post_rule = self.rule.get('post_rule')
        title_rule = post_rule.get('title')
        content_rule = post_rule.get('content')
        thumbnail_rule = post_rule.get('thumbnail')

        if type(url) == dict and url.get('url'):
            url = url.get('url')

        html = self.http.html(url)
        doc = pyquery.PyQuery(html)
        content = doc(content_rule)
        title = doc(title_rule).text()
        thumbnail = doc(thumbnail_rule)
        print('[%s/%s]' % (kwargs.get('i'), kwargs.get('n')), title, content, thumbnail, url)
        return [title, content, thumbnail]

    def execute(self, tasks: list, fn, callback=None, **kwargs):
        tasks.reverse()
        n = len(tasks)

        thread_num = kwargs.pop('thread_num', self.thread_num)
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
                except HttpException as he:
                    self.logger.exception(he)
                except Exception as e:
                    self.logger.exception(e)
        return result_list

    def process_time(self):
        self.logger.info("%s seconds process time" % (time.time() - self.begin_tme))

    def processing(self, _bar: Bar, title: str, status):
        with self.lock:
            if _bar:
                n = 0
                title = title.strip()
                for i in title:
                    if unicodedata.east_asian_width(i) in ('F', 'W'):
                        n += 2
                    else:
                        n += 1

                b = 64 - n
                c = ' ' * b
                d = '[\033[32m{}\033[0m' if status == 'done' else '\033[31m{}\033[0m'
                message = '[+]: %s%s[\033[%s]' % (title, c, d.format(status))
                _bar.writeln(message)
                _bar.finish()
            if self.bar:
                self.bar.next()

    def publish(self, data):
        res = self.http.html(self.publish_api, data)
        return res
