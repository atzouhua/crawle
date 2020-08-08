import argparse
import logging

from .libs.common import find_modules, run_client

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


def cli():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--page-url', type=str)
    parent_parser.add_argument('--start-page', type=int, default=1)
    parent_parser.add_argument('--end-page', type=int, default=1)
    parent_parser.add_argument('--chunk-size', type=int, default=1)
    parent_parser.add_argument('--action', type=str, default='index')
    parent_parser.add_argument('--detail-url', type=str)
    parent_parser.add_argument('--publish-url', type=str)
    parent_parser.add_argument('--test', action='store_true')
    parent_parser.add_argument('--debug', action='store_true')

    parser = argparse.ArgumentParser()
    modules = {}
    subparsers = parser.add_subparsers(dest="client")
    for module_name in find_modules('crawler.clients', False, True):
        name = module_name.split('.')[-1]
        subparsers.add_parser(name, parents=[parent_parser])
        modules[name] = module_name

    params = vars(parser.parse_args())
    client = params.get('client')
    if client:
        params['client'] = modules[client]

    if params.get('debug'):
        logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.DEBUG)

    run_client(**params)


if __name__ == '__main__':
    cli()
