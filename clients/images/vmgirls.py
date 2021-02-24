import random

from libs.base_client import BaseClient
from libs.common import format_url, format_view, md5
from libs.request import Request


class VmGirls(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.vmgirls.com'
        self.start_url = f'{self.base_url}/archives.html'

    def parse(self, response):
        doc = response.doc
        # elements = doc('.archives a')
        data = []
        for element in doc('.Recommended_Posts a.list-title').items():
            url = element.attr('href')
            if url.find('html') == -1:
                continue

            url = format_url(url, self.base_url)
            data.append(Request(url, self.parse_page))
        return data

    def parse_page(self, response):
        doc = response.doc

        title = doc('.post-title').text()
        image_list = []
        for item in doc('.nc-light-gallery img').items():
            image_list.append(item.attr('url'))

        tag_list = []
        for item in doc('.post-tags a').items():
            tag_list.append(item.text())

        _id = md5(title)
        return {
            '_id': _id,
            'title': title, 'image': image_list, 'tag': tag_list, 'url': response.url
        }
