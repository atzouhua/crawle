import hashlib
import inspect
import os
import pkgutil
import re
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

from .config import Config

load_dotenv()

DEV_ENV = os.environ.get('ENV_CODE', 'dev') == 'dev'


def md5(string: str):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    _md5 = m.hexdigest()
    return _md5[8:-8].upper()


def format_url(url: str, base_url: str):
    if url.find('http') != -1:
        return url
    if url.find('//') != -1:
        result = urlparse(base_url)
        return f'{result.scheme}:{url}'
    return '{}/{}'.format(base_url.strip('/'), url.strip('/'))


def get_terminal_size():
    return os.get_terminal_size()


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
    Config.batch_set(**kwargs)

    client = kwargs.get("client")
    module = import_string(kwargs.get('module'))

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and client.find(obj.__name__.lower()) != -1:
            instance = obj()
            action_name = kwargs.get('action')
            getattr(instance, 'before_action')()
            data = getattr(instance, f'action_{action_name}')()
            getattr(instance, 'after_action')()
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
