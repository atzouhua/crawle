import hashlib
import inspect
import os
import re
import socket
from concurrent import futures
from importlib import import_module
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

ROOT_PATH = dirname(dirname(dirname(realpath(__file__))))
DATA_PATH = os.path.join(ROOT_PATH, 'data')
LOG_PATH = os.path.join(DATA_PATH, 'logs')

if not os.path.isdir(DATA_PATH):
    os.makedirs(DATA_PATH)


def md5(string: str):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    _md5 = m.hexdigest()
    return _md5[8:-8].upper()


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
        return m.group(group)
    return default


def r2(pattern, text, repl='', default=None):
    if not text:
        return default
    return re.sub(pattern, repl, text, re.IGNORECASE | re.DOTALL).strip()


def get_item_name(origin_name: str):
    if r1(r'通知|付费|梦想|连更|公告|预热活动', origin_name, 0):
        return None
    # if r1(r'^第[\d]+话$', origin_name, 0):
    #     return ''
    # new_name = r1(r'第[\d]+话(.+)', origin_name, 1)
    # if new_name:
    #     return new_name
    # new_name = r1('^[0-9]*$', origin_name, 0)
    # if new_name:
    #     return ''
    return origin_name


def run_handler(module_name, action_name, **kwargs):
    for key in list(kwargs.keys()):
        if not kwargs.get(key):
            del kwargs[key]

    module = import_module('.'.join(['crawler', 'handlers', module_name]))
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__bases__[0].__name__ == 'BaseHandler':
            instance = obj()
            instance.config = kwargs
            getattr(instance, f'action_before')()
            getattr(instance, f'action_{action_name}')()
            getattr(instance, f'action_after')()
            break


def get_page_url_list(**kwargs):
    tasks = []
    page_url = kwargs.get('url') or kwargs.get('page_url')
    base_url = kwargs.get('base_url')

    start_page = kwargs.get('start_page') or 1
    end_page = kwargs.get('end_page') or 1

    if end_page < start_page:
        end_page = start_page

    for i in range(start_page, end_page + 1):
        url = page_url.replace('%page', str(i))
        tasks.append(format_url(url, base_url))

    tasks.reverse()
    return tasks


def format_view(views):
    if views.find('亿') != -1:
        views = float(views.replace('亿', '')) * 100000000 / 100
    elif views.find('万') != -1:
        views = float(views.replace('万', '')) * 10000 / 100
    return int(views)
