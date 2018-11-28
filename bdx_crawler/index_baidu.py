# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    index_baidu
   Description :
   Author :       changsk
   date：          2018/10/30
-------------------------------------------------
   Change Activity:
                   2018/10/30:
-------------------------------------------------
"""
import os
import time
import functools
import multiprocessing
import uuid

import arrow
import pandas as pd
import click

from .utils import Crawler, split_groups
from .config import raw_config


def index_crawl(kws, date1, date2, terminal='both', processes=4, debug=0):
    start = time.time()

    begin = arrow.get(date1)
    end = arrow.get(date2)
    processes = int(processes) if isinstance(processes, str) else processes
    debug = int(debug) if isinstance(debug, str) else debug

    delta = (end - begin).days + 1
    all_days = [a.format('YYYY-MM-DD') for a in arrow.Arrow.range('day', begin, end)]
    date_groups = split_groups(begin, end)
    click.echo(f'basic info <kws:{kws}>, <date:{all_days[0]}-{all_days[-1]}>,<{terminal}>')

    tdf = pd.DataFrame()
    errs = []
    step = 5
    kws = kws.split(',')
    kws, undefined = Crawler.filter_valid_kws(kws)
    kw_group = [kws[i:i+step] for i in range(0,len(kws),step)]
    click.echo(f'共有{len(kws)}词需要爬取, 拆分为{len(kw_group)}个子任务')
    pool = multiprocessing.Pool(processes)
    single_task = functools.partial(single_crawl, date_groups, terminal=terminal, debug=debug)
    iterable = pool.imap(single_task, kw_group)

    with click.progressbar(iterable, len(kw_group)) as bar:
        for df, undefined_kws in bar:

            if len(df) > 0:
                df = df.drop_duplicates(['date'])
                df = df.set_index('date')
                file_name = f"{'-'.join(df.columns.tolist())}_{terminal}_{uuid.uuid4()}.xlsx"
                df.to_excel(os.path.join(raw_config['temp_path'], file_name), encoding='utf-8')
                if len(undefined_kws) > 0:
                    undefined.extend(undefined_kws)
                    click.echo(f'下列关键词未被百度指数收录: {undefined_kws}')
                tdf = pd.concat([tdf,df],axis=1)
            else:
                click.echo(f'single_crawl failed {undefined_kws}')
                errs.extend(undefined_kws)

    click.echo('**************RESULT**************************')
    click.echo(f'done, total cost time: {time.time()-start}')
    miss_days = set(all_days).difference(tdf.index.tolist())
    click.echo(f'共{delta}天数据,已抓取{len(tdf)}天')
    if len(undefined) > 0:
        click.echo(f'{len(undefined)}个关键词未被百度指数收录: {undefined}')
    if len(errs) > 0:
        click.echo(f'{len(errs)}个关键词抓取失败,请重新尝试: {errs}')
    if delta <= len(tdf):
        click.echo('所有日期都已经成功抓取了!')
    else:
        click.echo('以下日期未能成功抓取....')
        for idx, value in enumerate(miss_days):
            click.echo(f'{idx}: {value}')
    return tdf


def single_crawl(date_groups, kw, terminal='both', debug=False):
    crawler = Crawler(debug=debug)
    click.echo(f'now we crawl for {kw}')
    df = pd.DataFrame()
    valid, undefined_kws = crawler.check_validation(kw)
    if not valid:
        if len(undefined_kws) > 0:
            kw = [k for k in kw if k.lower() not in undefined_kws]
            if len(kw) == 0:
                click.echo(f'{len(undefined_kws)}个关键词未被百度指数收录: {undefined_kws}')
                crawler.quit()
                return df, undefined_kws
            else:
                crawler.check_validation(kw)
        else:
            click.echo('页面加载失败')
            crawler.quit()
            return df, kw

    time.sleep(3)
    state = crawler.set_terminal(terminal)
    if not state:
        click.echo('终端选择错误, 退出')
        crawler.quit()

        return df, kw

    for date1, date2 in date_groups:
        try:
            # click.echo(f'时间段{date1}-{date2}的数据')
            state = crawler.set_date_range(date1, date2)
            if state:
                click.echo(f'正在解析 <{kw}> 时间段 {date1}-{date2} 的数据')
                df = pd.concat([df, crawler.fetch_all_data(kw)])
            elif not state:
                click.echo(f'时间设置错误, 跳过')
        except Exception as e:
            click.echo(f'error happend <{kw}>: {date1}-{date2}, {e}')
    crawler.quit()
    return df, undefined_kws
