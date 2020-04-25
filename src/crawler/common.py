import os
import re
import socket
from os.path import dirname, realpath

from progress.bar import Bar

from .utils.config import Config

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

if ip.find('10.3.19') != -1 or ip.find('192.168') != -1 or ip.find('10.0.2') != -1:
    SS_PROXIES = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080',
    }
else:
    SS_PROXIES = None

ROOT_PATH = dirname(dirname(dirname(realpath(__file__))))
DATA_PATH = os.path.join(ROOT_PATH, 'data')
LOG_PATH = os.path.join(DATA_PATH, 'logs')

if not os.path.isdir(DATA_PATH):
    os.makedirs(DATA_PATH)


def format_url(url: str, base_url: str):
    if url.find('http') == -1:
        url = '{}/{}'.format(base_url.strip('/'), url.strip('/'))
    return url


def get_tasks(rule: dict):
    tasks = []
    page_url = Config.get('url')
    base_url = rule.get('base_url')
    if page_url:
        tasks.append(format_url(page_url, base_url))
    else:
        if rule.get('append_page_list_url'):
            tasks.append(rule.get('append_page_list_url'))

        start_page = Config.get('start', rule.get('start_page', 1))
        end_page = Config.get('end', rule.get('end_page', 1))

        if end_page < start_page:
            end_page = start_page + 1

        page_url = rule.get('page_list_url')
        for i in range(start_page, end_page + 1):
            url = page_url.replace('%page', str(i))
            tasks.append(format_url(url, base_url))

    tasks.reverse()
    return tasks


def get_progress_bar(_max) -> Bar:
    suffix = '%(percent)d%% [%(index)d/%(max)d] %(elapsed_td)s'
    bar_prefix = ' ['
    bar_suffix = '] '
    return Bar('Processing', max=_max, suffix=suffix,
               bar_prefix=bar_prefix,
               bar_suffix=bar_suffix)


def get_book_item_name(item_name, exclude_list=None):
    r = re.search('^[0-9]*$', item_name)
    if r:
        item_name = '第%s话' % item_name
    return item_name


def r1(pattern, text, group=1, default=None):
    if not text or type(text) != str:
        return default

    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return m.group(group).strip()
    return default


def r2(pattern, text, repl=''):
    if not text:
        return None

    return re.sub(pattern, repl, text, re.IGNORECASE).strip()
