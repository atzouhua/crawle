import logging

import click

import crawler
from crawler.libs.common import run_handler

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


@click.group(invoke_without_command=True)
@click.argument('handler', nargs=1, default='sousi')
@click.option('--start-page', type=int, default=1)
@click.option('--end-page', type=int, default=1)
@click.option('--page-url', type=str)
@click.option('--test', is_flag=True)
@click.option('-P', '--progress', is_flag=True, help='debug mode')
@click.option('--debug', is_flag=True)
@click.option('--version', default=crawler.__version__)
@click.pass_context
def cli(ctx, **kwargs):
    if kwargs.get('debug'):
        logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.DEBUG)

    ctx.obj = kwargs
    if ctx.invoked_subcommand is None:
        _run(ctx, 'index', **kwargs)


@cli.command()
@click.option('--url', type=str, required=True, default='http://www.sosi55.com/guochantaotu/disi/2014/0415/19771.html')
@click.pass_context
def detail(ctx, **kwargs):
    _run(ctx, 'detail', **kwargs)


@cli.command()
@click.argument('action_name', nargs=1)
@click.pass_context
def action(ctx, action_name):
    _run(ctx, action_name)


def _run(ctx, action_name, **kwargs):
    kwargs.update(ctx.obj)
    run_handler(kwargs.get('handler'), action_name, **kwargs)


if __name__ == '__main__':
    cli()
