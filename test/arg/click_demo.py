#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def cli():
    pass


@cli.command()
@click.argument('name', default='all', required=True)
def hellocmd(name):
    """ 打印帮助信息 """
    click.echo(
        click.style(
            'I am colored %s and bold' %
            name,
            fg='green',
            bold=True))

    print "done!"


@cli.command()
@click.option('-t', default='a', required=True,
              type=click.Choice(['a', 'h']), prompt=True, help='检测类型，a表示所有空间，h表示空间大于50%')
def dfcmd(t):
    """
    检查磁盘空间 dfcmd
    """
    click.echo(click.style('检查磁盘空间', fg='green', bold=True))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('x', type=int, required=True)
def square(x):
    """
    得到x平方 square x
    """
    click.echo(click.style('x= %s' % x, fg='green', bold=True))
    print(x * x)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('path', type=click.Path(exists=True))
def touch(path):
    """ 创建一个文件 """
    click.echo(click.format_filename(path))


if __name__ == '__main__':
    cli()
