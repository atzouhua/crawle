import inspect
import logging
import os
import time
from logging import FileHandler

from crawler.common import LOG_PATH

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'

# logging.basicConfig(format=DEFAULT_FORMATTER)
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     datefmt='%a, %d %b %Y %H:%M:%S')


class BaseFileHandler(FileHandler):

    def __init__(self):
        FileHandler.__init__(self, 'test', 'a', 'utf-8', True)

    def emit(self, record):
        log_path = os.path.join(LOG_PATH, record.levelname)
        if not os.path.isdir(log_path):
            os.makedirs(log_path)

        name = time.strftime("%Y-%m-%d", time.localtime())

        filename = '%s/%s.log' % (log_path, name)
        self.baseFilename = filename
        self.stream = self._open()

        FileHandler.emit(self, record)

        if self.stream:
            self.close()


def get_current_function_name():
    return inspect.stack()[-1][1]


class Logging:
    file_handle = BaseFileHandler()
    file_handle.setFormatter(logging.Formatter(DEFAULT_FORMATTER))
    file_handle.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(DEFAULT_FORMATTER))
    console.setLevel(logging.DEBUG)

    @classmethod
    def get(cls, name=None):
        if not name:
            name = get_current_function_name()

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(cls.file_handle)
        logger.addHandler(cls.console)
        return logger
