#!/usr/bin/python
# -*- coding: UTF-8 -*-
import click


@click.group()
def gpfun():
    pass


@click.command()
@click.option('--name', help='你的名字', required=True)
def hello(name):
    """ 打印 hello, world 信息 """
    click.echo('Hello World! hello %s' % name)


@click.command()
@click.option('--name', help='测试名字', required=True)
def test(name):
    """ 测试命令 """
    click.echo('Hello World! hello %s' % name)


gpfun.add_command(hello)
gpfun.add_command(test)

if __name__ == '__main__':
    gpfun()
