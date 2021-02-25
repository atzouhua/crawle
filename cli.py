import argparse
import logging

from libs.common import find_modules, run_client

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


def cli():
    modules = {}
    for module_name in find_modules('clients', False, True):
        name = module_name.split('.')[-1]
        modules[name] = module_name

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('client')
    parser.add_argument('--start-url', type=str)
    parser.add_argument('--start-page', type=int, default=1)
    parser.add_argument('--end-page', type=int, default=1)
    parser.add_argument('--chunk-size', type=int, default=1)
    parser.add_argument('--thread')
    parser.add_argument('--debug', action='store_true')

    params = vars(parser.parse_args())
    client = params.get('client')

    module = modules.get(client)
    if not module:
        parser.print_usage()
        exit()

    params['module'] = module

    if params.get('debug'):
        logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.DEBUG)

    run_client(**params)


if __name__ == '__main__':
    cli()
