import codecs
import os

import requests


class FileHelper:

    @classmethod
    def read_file(cls, file):
        if os.path.isfile(file):
            with codecs.open(file, encoding='utf-8') as f:
                data = f.read()
            return data
        return None

    @classmethod
    def write_file(cls, file, data, mode='w'):
        if len(data):
            with codecs.open(file, mode, 'utf-8') as f:
                f.write(data)
                if mode.find('+') != -1:
                    f.write('\n')

    @classmethod
    def down_file(cls, url, file_name):
        if not os.path.isfile(file_name):
            response = requests.get(url)
            with open(file_name, 'wb') as f:
                f.write(response.content)

        return file_name
