import os
import time

import pymongo

from .base_crawle import BaseCrawler
from .common import format_url, md5
from .request import Request


class BaseClient(BaseCrawler):

    def __init__(self):
        super(BaseClient, self).__init__()
        self.begin_tme = time.perf_counter()
        self.rule = {}
        self.config = {}
        self.client = None

    def get_db(self, db='db1'):
        if not self.client:
            self.client = pymongo.MongoClient(os.environ.get('MONGO_URI'), connectTimeoutMS=10000)
        return self.client.get_database(db)

    def before_run(self):
        pass

    def after_run(self):
        self.process_time()
        if self.client:
            self.client.close()

    def run(self):
        data = self.crawl(self.get_start_url_list())
        while 1:
            if len(data) <= 0 or type(data[0]) != Request:
                break
            data = self.crawl(data, thread=self.config.get('thread'), chunk_size=self.config.get('chunk_size'))
        self.save(data)

    def save(self, data):
        pass

    def do_save(self, data, col, key='title'):
        db = self.get_db()
        col = db.get_collection(col)
        for item in data:
            _id = md5(item[key])
            col.update_one({'_id': _id}, {'$set': item}, True)

    def parse(self, response):
        page_rule = self.rule.get('page_rule')
        doc = response.doc
        data = []
        for element in doc(page_rule.get('list')).items():
            url = element.attr('href')
            url = format_url(url, self.rule.get('base_url'))
            data.append(Request(url, self.parse_page))
        return data

    def parse_page(self, response):
        pass

    def process_time(self):
        self.logger.info("process time {:.2f}s".format(time.perf_counter() - self.begin_tme))

    def get_start_url_list(self):
        if hasattr(self, 'start_url'):
            return [Request(self.start_url, self.parse)]

        page_url = self.config.get('start_url') or self.rule.get('start_url')
        start_page = self.config.get('start_page') or self.rule.get('start_page')
        end_page = self.config.get('end_page') or self.rule.get('end_page')

        if end_page < start_page:
            end_page = start_page

        data = []
        for i in range(start_page, end_page + 1):
            self.logger.info(f'fetch page {i}.')
            url = page_url.replace('%page', str(i))
            data.append(Request(format_url(url, self.rule.get('base_url')), self.parse))
        return data
