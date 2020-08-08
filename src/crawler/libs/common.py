import hashlib
import inspect
import logging
import os
import pkgutil
import re
import sys
from importlib import import_module

from dotenv import load_dotenv
from progress.bar import Bar

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)

load_dotenv()

PG_PASSWORD = os.environ.get('PG_PASSWORD')
DEV_ENV = os.environ.get('ENV_CODE', 'dev') == 'dev'


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


def r3(pattern, text, group=1, default=None):
    if not text or type(text) != str:
        return default

    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        groups = m.groups()
        return groups[group]
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


def run_client(**kwargs):
    module = import_string(kwargs.get("client"))
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__bases__[0].__name__ == 'BaseClient':
            instance = obj()
            for k, v in kwargs.items():
                setattr(instance, k, v)

            action_name = kwargs.get('action')
            getattr(instance, f'action_before')()
            data = getattr(instance, f'action_{action_name}')()
            getattr(instance, f'action_after')()
            return data


def format_view(views):
    if views.find('亿') != -1:
        views = float(views.replace('亿', '')) * 100000000 / 100
    elif views.find('万') != -1:
        views = float(views.replace('万', '')) * 10000 / 100
    return int(views)


def import_string(import_name, silent=False):
    import_name = str(import_name).replace(":", ".")
    try:
        try:
            __import__(import_name)
        except ImportError:
            if "." not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit(".", 1)
        module = __import__(module_name, globals(), locals(), [obj_name])
        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)
    except ImportError as e:
        raise e


def find_modules(import_path, include_packages=False, recursive=False):
    module = import_string(import_path)
    path = getattr(module, "__path__", None)
    if path is None:
        raise ValueError("%r is not a package" % import_path)
    basename = module.__name__ + "."
    for _importer, modname, ispkg in pkgutil.iter_modules(path):
        modname = basename + modname
        if ispkg:
            if include_packages:
                yield modname
            if recursive:
                for item in find_modules(modname, include_packages, True):
                    yield item
        else:
            yield modname
