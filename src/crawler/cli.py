import argparse
import inspect
import logging
from importlib import import_module

from crawler.extractors.base import BaseCrawler
from crawler.utils.config import Config


def script_main():
    crawler = Config.get('crawler')
    m = import_module('.'.join(['crawler', 'extractors', crawler]))
    if not m:
        logging.info('No crawler %s was found' % crawler)
        return

    try:
        for name, obj in inspect.getmembers(m):
            if inspect.isclass(obj) and issubclass(obj, BaseCrawler) and name != 'BaseCrawler':
                instance = obj()
                instance.before_run()
                instance.run()
                instance.after_run()
                break
    except Exception as e:
        logging.exception(e)


def app_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('crawler', nargs='?', default='sehuatang')
    parser.add_argument('action', nargs='?', default='')
    parser.add_argument('url', nargs='?', default='')
    parser.add_argument('-t', '--thread', type=int, default=10)
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--cid', type=int, default=2)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--disable-bar', action='store_true')

    parsed_args = parser.parse_args()
    params = vars(parsed_args)
    if params.get('crawler') is None:
        print('Please select a crawler')
        return

    Config.batch_set(**vars(parsed_args))
    script_main()


def main():
    app_main()


if __name__ == '__main__':
    main()
