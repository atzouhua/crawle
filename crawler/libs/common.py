import os
import re
import socket
from os.path import dirname, realpath

from progress.bar import Bar

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

if ip.find('10.3.19') != -1 or ip.find('192.168') != -1 or ip.find('10.0.2') != -1:
    HTTP_PROXIES = {
        'http': 'http://127.0.0.1:1081',
        'https': 'http://127.0.0.1:1081',
    }
else:
    HTTP_PROXIES = None

ROOT_PATH = dirname(dirname(dirname(dirname(realpath(__file__)))))
DATA_PATH = os.path.join(ROOT_PATH, 'data')
LOG_PATH = os.path.join(DATA_PATH, 'logs')

if not os.path.isdir(DATA_PATH):
    os.makedirs(DATA_PATH)


def format_url(url: str, base_url: str):
    if url.find('http') == -1:
        url = '{}/{}'.format(base_url.strip('/'), url.strip('/'))
    return url


def get_terminal_size():
    return os.get_terminal_size()


def get_progress_bar(_max) -> Bar:
    suffix = '%(percent)d%% [%(index)d/%(max)d] %(elapsed_td)s'
    bar_prefix = ' ['
    bar_suffix = '] '
    return Bar('Processing', max=_max, suffix=suffix,
               bar_prefix=bar_prefix,
               bar_suffix=bar_suffix)


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
    return re.sub(pattern, repl, text, re.IGNORECASE | re.DOTALL).strip()
