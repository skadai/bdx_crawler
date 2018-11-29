# -*- coding: utf-8 -*-

# @File    : command_line.py
# @Date    : 2018-11-28
# @Author  : skym
__author__ = 'changsk'

import click
import os
import json

from .index_baidu import index_crawl, reset_cookie
from .utils import load_config


ROOT_DIR = os.path.dirname(__file__)


@click.group()
def cli():
    """
    百度指数爬虫
    """
    pass


@cli.command()
@click.option('-w', '--kws', required=True, help='待查询关键词, 英文逗号,分开')
@click.option('-b', '--date1', default='2018-01-01', help='起始日期,默认2018-01-01')
@click.option('-e', '--date2', default='2018-11-11', help='结束日期,示例2018-11-11')
@click.option('-t', '--terminal', default='both', help='终端类型: pc/mobile/both, 默认both')
@click.option('-o', '--file_path', required=True, help='结果文件路径, 只支持xlsx')
@click.option('-n', '--processes', default=4, help='进程数目, 默认为4')
@click.option('-p', '--province', default='全国', help='省份, 默认全国')
@click.option('-d', '--debug', is_flag=True, help='是否为debug模式,默认关闭')
def crawl(kws, date1, date2, file_path, province, terminal, processes, debug):
    """
    输入参数进行百度指数抓取
    """
    tdf = index_crawl(kws, date1, date2, province, terminal, processes, debug)
    tdf.to_excel(file_path, encoding='utf-8')
    click.echo(f'详细结果请前往 {file_path} 查看')


@cli.command()
@click.argument('config_file', required=True)
def crawlf(config_file):
    """
    根据文件配置进行百度指数抓取, 文件配置参考crawl_sample
    """
    raw_config = load_config(config_file)
    file_path = raw_config.pop('file_path')
    tdf = index_crawl(**raw_config)
    tdf.to_excel(file_path, encoding='utf-8')
    click.echo(f'详细结果请前往 {file_path} 查看')


@cli.command()
def repair():
    """
    引导用户进行cookie重新设置
    """
    file_path = os.path.join(ROOT_DIR, 'secret')
    valid, cookies = reset_cookie()
    if valid:
        with open(file_path, 'w', encoding='utf-8') as c:
            c.write(json.dumps(cookies))
        click.echo('恭喜你已经重新设置了cookie')
    else:
        click.echo('oops,出了点问题,你可以尝试手动替换cookie')
        click.echo(f'从浏览器复制百度cookie原始字符串覆盖文件{file_path}内容就好了')



if __name__ == '__main__':
    cli()
