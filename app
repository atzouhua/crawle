#!/usr/bin/env python3
import argparse
import inspect
import logging
from importlib import import_module

from crawler.libs.base import BaseHandler

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


def script_main(config: dict):
    crawler = config.get('craw')
    m = import_module('.'.join(['crawler', 'handlers', crawler]))
    if not m:
        logging.info('No crawler %s was found' % crawler)
        return

    try:
        for name, obj in inspect.getmembers(m):
            if inspect.isclass(obj) and issubclass(obj, BaseHandler) and name != 'BaseHandler':
                instance = obj()
                instance.config = config
                instance.before_run()
                instance.run()
                instance.after_run()
                break
    except Exception as e:
        logging.exception(e)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('craw', nargs='?', default='mkzhan')
    parser.add_argument('action', nargs='?')
    parser.add_argument('url', nargs='?')
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--cid', type=int)
    parser.add_argument('--test', action='store_true')

    parsed_args = vars(parser.parse_args())
    for key in list(parsed_args.keys()):
        if not parsed_args.get(key):
            del parsed_args[key]
    script_main(parsed_args)


if __name__ == '__main__':
    cli()

    # scale = 80
    #
    # start = time.perf_counter()
    # for i in range(scale + 1):
    #     a = '#' * i  # i 个长度的 * 符号
    #     b = '-' * (scale - i)  # scale-i） 个长度的 . 符号。符号 * 和 . 总长度为50
    #     c = (i / scale) * 100  # 显示当前进度，百分之多少
    #     dur = time.perf_counter() - start  # 计时，计算进度条走到某一百分比的用时
    #     print("\r{:^3.0f}%[{}{}]{:.2f}s".format(c, a, b, dur),
    #           end='')  # \r用来在每次输出完成后，将光标移至行首，这样保证进度条始终在同一行输出，即在一行不断刷新的效果；{:^3.0f}，输出格式为居中，占3位，小数点后0位，浮点型数，对应输出的数为c；{}，对应输出的数为a；{}，对应输出的数为b；{:.2f}，输出有两位小数的浮点数，对应输出的数为dur；end=''，用来保证不换行，不加这句默认换行。
    #     time.sleep(0.1)
