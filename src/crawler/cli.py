import argparse
import logging
from importlib import import_module

# pip3 install requests pyquery progress opencc-python-reimplemented
from .utils.config import Config

class_map = {
}


def script_main():
    crawler = Config.get('crawler')
    m = import_module('.'.join(['crawler', 'extractors', crawler]))
    if not m:
        logging.info('No crawler %s was found' % crawler)
        return

    class_name = class_map.get(crawler)
    if not class_name:
        class_name = crawler.title()

    try:
        obj = getattr(m, class_name)
        instance = obj()
        instance.before_run()
        instance.run()
        instance.after_run()
    except Exception as e:
        logging.exception(e)


def app_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('crawler', nargs='?', default='sousi8')
    parser.add_argument('action', nargs='?')
    parser.add_argument('url', nargs='?')
    parser.add_argument('-t', '--thread', type=int, default=10)
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--cid', type=int)
    parser.add_argument('--test', action='store_true')

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
