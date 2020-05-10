import asyncio
import itertools
import logging
import time

import pyquery
import uvloop
from aiohttp import ClientSession

from .db import DB
from .common import format_url, HTTP_PROXIES


class BaseHandler:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        self.proxies = HTTP_PROXIES
        self.charset = 'utf-8'
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = {}
        self.rule = {}
        self.result = []
        self.tasks = []

        self.begin_tme = time.perf_counter()
        self.table = ''

    def before_run(self):
        pass

    def after_run(self):
        if len(self.result):
            DB.insert_all(self.table, self.result)
            self.result = []
        self.process_time()

    def run(self):
        _action = 'action_{}'.format(self.config.get('action', 'index'))
        if hasattr(self, _action):
            func = getattr(self, _action)
            func()

    def action_index(self):
        url_list = self.get_index_url_list()
        n = len(url_list)
        if not n:
            self.logger.warning('empty url list.')
            return

        tasks = self.crawl(url_list)
        task_count = len(tasks)
        self.logger.info(f'task count: {task_count}')

        if task_count:
            self.crawl(tasks, self.detail_handler, self.on_result)

    def crawl(self, tasks: list, task_handler=None, callback=None, semaphore_count=100):
        if not task_handler:
            task_handler = self.page_handler

        main_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(main_loop)
        semaphore = asyncio.Semaphore(semaphore_count)
        n = len(tasks)

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        new_tasks = []

        async def _run():
            async with semaphore:
                async with ClientSession() as session:
                    for i, task in enumerate(tasks):
                        future = asyncio.ensure_future(task_handler(task, i=i + 1, n=n, session=session))
                        if callback:
                            future.add_done_callback(callback)
                        new_tasks.append(future)
                    return await asyncio.gather(*new_tasks)

        try:
            result = main_loop.run_until_complete(_run())
            if len(result) > 1:
                return [x for j in result for x in j]
            return result
        except Exception as e:
            logging.exception(e)
            return None
        finally:
            if not main_loop.is_closed():
                main_loop.close()

    async def get_html(self, session, url, method='GET', callback=None, **kwargs):
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('verify_ssl', False)
        kwargs.setdefault('proxy', self.proxies)
        kwargs.setdefault('headers', self.headers)
        ex = None

        for i in range(3):
            try:
                async with session.request(method, url, **kwargs) as response:
                    html = await response.text(encoding=self.charset)
                    if callback:
                        return callback(html)
                    return html
            except Exception as e:
                ex = e
                await asyncio.sleep(1)
        raise ex

    async def doc(self, url, session, method='GET', **kwargs):
        if type(url) == dict:
            url = url.get('url')
        return pyquery.PyQuery(await self.get_html(session, url, method, **kwargs))

    async def page_handler(self, task, session, **kwargs):
        title_rule = self.page_rule.get('title')
        thumbnail_rule = self.page_rule.get('thumbnail')

        self.logger.info('[%s/%s] Get page: %s' % (kwargs.get('i'), kwargs.get('n'), task))
        doc = await self.doc(task, session)
        elements = doc(self.page_rule.get('list'))
        result = []
        for element in elements.items():
            title = element.text()
            url = format_url(element.attr('href'), self.rule.get('base_url'))
            thumbnail = ''

            if title_rule:
                title = element(title_rule).text()
            if thumbnail_rule:
                thumbnail = element(thumbnail_rule).attr('src')
            data = {'title': title, 'url': url, 'thumbnail': thumbnail}
            result.append(data)
        return result

    async def detail_handler(self, task, session, **kwargs):
        if type(task) == dict:
            task = task.get('url')
        try:
            doc = await self.doc(task, session)
            for field, rule in self.post_rule.items():
                if field == 'thumbnail':
                    kwargs[field] = doc(rule).attr('src')
                else:
                    kwargs[field] = doc(rule).text()
            kwargs.setdefault('doc', doc)
            return kwargs
        except Exception as e:
            logging.exception(e)

    def process_time(self):
        self.logger.info("process time {:.2f}s".format(time.perf_counter() - self.begin_tme))

    def processing(self, i, n, message):
        self.logger.info(f"[{i}/{n}]:{message}")

    def on_result(self, future):
        result = future.result()
        result_info = result[1]
        self.processing(result_info['i'], result_info['n'], result[0]['title'])

    def save(self, params, message, db_save=True, **kwargs):
        self.processing(kwargs.get('i'), kwargs.get('n'), message)
        if db_save:
            self._db_save(params)

    def _db_save(self, params: dict):
        self.result.append(params)
        if len(self.result) >= 50:
            DB.insert_all(self.table, self.result)
            self.result = []

    @property
    def post_rule(self):
        return self.rule.get('post_rule')

    @property
    def page_rule(self):
        return self.rule.get('page_rule')

    def get_index_url_list(self):
        tasks = []
        page_url = self.config.get('url')
        base_url = self.rule.get('base_url')
        if not page_url:
            page_url = self.rule.get('page_url')
            if self.rule.get('append_page_url'):
                tasks.append(format_url(self.rule.get('append_page_url'), base_url))

        start_page = self.config.get('start', self.rule.get('start_page', 1))
        end_page = self.config.get('end', self.rule.get('end_page', 1))

        if end_page < start_page:
            end_page = start_page + 1

        for i in range(start_page, end_page + 1):
            url = page_url.replace('%page', str(i))
            if url.find('%cid') != -1:
                url = url.replace('%cid', str(self.config.get('cid')))
            tasks.append(format_url(url, base_url))

        tasks.reverse()
        return tasks
