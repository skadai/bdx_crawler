import os
import time
import math
import re

import arrow
import pandas as pd
import urllib
import click
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from config import raw_cookie, raw_kws


class Crawler:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://index.baidu.com/v2/main/index.html#/trend/{}?words={}"
        self.max_try = 3
        self.base_cookie = {}
        self.ranger = {}
        self.driver.get('http://index.baidu.com')
        self.flag = 0
        self.confirm = 1
        self.format_cookies()
        self.replace_cookies()

    def format_cookies(self):
        for item in raw_cookie.split(';'):
            kv = item.strip().split('=')
            self.base_cookie[kv[0]] = '='.join(kv[1:])

    def replace_cookies(self):
        self.driver.delete_all_cookies()
        for k, v in self.base_cookie.items():
            self.driver.add_cookie({'name': k, 'value': v})

    def make_url(self, keywords):
        words = []
        for kw in keywords:
            words.append(urllib.parse.quote(kw.encode('utf-8')))
        url = self.base_url.format(words[0], ','.join(words))
        return url

    def check_validation(self, kws):
        url = self.make_url(kws)
        click.echo(url)
        self.driver.get(url)
        count, charts = 0, []
        # 需要确认已拿到百度指数的数据
        while count < self.max_try:
            try:
                # 此处判据有问题
                charts = self.driver.find_elements_by_css_selector('.index-trend-chart')
                if len(charts) > 0:
                    break
            except Exception as e:
                click.echo(f'还没有加载出来页面...{e}')
                self.driver.get(url)
                time.sleep(3)
            count += 1

        if len(charts) == 0:
            click.echo('加载页面失败....')
            return False, []

        try:
            text = self.driver.find_element_by_class_name('words').text
            return False, text.split(',')
        except Exception as e:
            return True, []


    def fetch_all_data(self, kws):
        date_picker = self.driver.find_element_by_class_name('index-date-range-picker')
        start, end = date_picker.text.split('~')
        click.echo(f'start:{start}, end: {end}')
        start = start.strip()
        end = end.strip()
        xoyelement = self.driver.find_elements_by_css_selector('.index-trend-chart')[0]
        x, y = -1, 250

        days = (arrow.get(end)-arrow.get(start)).days
        delta = math.ceil(365 / days * 2)
        click.echo(f'当前的天数{days}是使用的扫描步频是,{delta}')
        datas = []

        err_count = 0
        while 1:
            if x > 2000 or err_count > 20:
                click.echo(f'循环次数过多, 跳出<x: {x}>')
                break

            ret = self.move_cursor(xoyelement, x, y)
            if len(ret) > 2:
                # click.echo(f'解析出的ret: {ret}')
                err_count = 0
                ret[0] = ret[0].split(' ')[0]
                if len(datas) == 0:
                    datas.append(ret[0::2])
                    click.echo(f'add, {ret[0::2]}, ---x-cord {x}')
                    x += delta

                elif ret[0].startswith(end):
                    datas.append(ret[0::2])
                    click.echo(f'已拿到最终数据 {ret[0::2]},跳出: --x-cord {x}')
                    break
                elif arrow.get(datas[-1][0]) == arrow.get(end).shift(days=-1):
                    click.echo('快到终点，调整delta')
                    x += delta/4

                else:
                    cur_date = arrow.get(ret[0])
                    last_date = arrow.get(datas[-1][0])
                    if cur_date > last_date.shift(days=1):
                        x -= delta/2
                        click.echo(f'日期不连续, 需后退... --x-cord {x}')
                    elif cur_date == last_date.shift(days=1):
                        datas.append(ret[0::2])
                        click.echo(f'add, {ret[0::2]}, ---x-cord {x}')
                        x += delta
                    else:
                        x += delta
            else:
                click.echo(f'没有解析出日期,进行下一次扫描')
                err_count += 1
                x += delta

        df = pd.DataFrame(datas, columns=['date']+kws)
        click.echo(f'图中的天数是{days},已抓取{len(df)}')
        return df

    def initiate_ranger(self):
        ynn, cury, ypp = self.driver.find_elements_by_class_name('veui-calendar-left')[self.flag].find_elements_by_css_selector('button')
        if cury.text == '' and self.flag > 1:
            print('当前flag错误')
            self.flag = self.flag - 2
            self.confirm = 0
            ynn, cury, ypp = self.driver.find_elements_by_class_name('veui-calendar-left')[self.flag].find_elements_by_css_selector('button')

        mnn, curm, mpp = self.driver.find_elements_by_class_name('veui-calendar-right')[self.flag].find_elements_by_css_selector('button')
        day_ranger = self.driver.find_elements_by_css_selector('.veui-calendar-body')[self.flag].find_elements_by_css_selector('.veui-calendar-day')
        self.ranger = dict(
            ynn=ynn,
            cury=cury,
            ypp=ypp,
            mnn=mnn,
            curm=curm,
            mpp=mpp,
            days=day_ranger
        )
        print('ranger解析年结果',cury.text)

    def refresh_ranger(self):
        self.ranger['days'] = self.driver.find_elements_by_css_selector('.veui-calendar-body')[self.flag].find_elements_by_css_selector('.veui-calendar-day')


    def set_terminal(self, terminal):
        if terminal == 'both':
            return True
        if terminal == 'mobile':
            idx = 2
        else:
            idx = 1
        self.driver.find_elements_by_class_name('index-dropdown-list')[1].click()
        click.echo('正在打开终端选项,请稍候...')
        count = 0
        time.sleep(2)
        while count < self.max_try:
            try:
                options = self.driver.find_elements_by_css_selector('.list-wrapper')[1]
                options.find_elements_by_class_name('list-item')[idx].click()
                return True
            except Exception as e:
                click.echo(f'try time {count}: sth wrong {e}')
                self.driver.find_elements_by_class_name('index-dropdown-list')[1].click()
                time.sleep(1)
                self.driver.find_elements_by_class_name('index-dropdown-list')[1].click()
                time.sleep(2)
                count += 1
        return False


    def set_date_range(self, date1, date2):
        # 点击下拉列表
        count = 0
        self.driver.find_element_by_class_name('index-date-range-picker').click()
        click.echo('正在打开时间选项,请稍候...')
        time.sleep(2)
        while count < self.max_try:
            try:
                # 设置日期
                self.set_date('begin', date1)
                self.set_date('end', date2)

                # 点击确认按钮
                self.driver.find_elements_by_css_selector('.primary')[self.confirm].click()
                time.sleep(3)
                return True
            except Exception as e:
                click.echo(f'try time {count}: sth wrong {e}')
                self.driver.find_element_by_class_name('index-date-range-picker').click()
                time.sleep(1)
                self.driver.find_element_by_class_name('index-date-range-picker').click()
                time.sleep(2)
                count += 1
        return False

    def move_cursor(self, obj, x, y):
        ActionChains(self.driver).move_to_element_with_offset(obj,x,y).perform()
        ret = obj.find_elements_by_css_selector('div:last-child')[0].text.split('\n')
        return ret

    def set_date(self, label, date):
        click.echo(f'now we set date....{label},{date}')
        idx = 0 if label == 'begin' else 1
        self.flag = idx + 2
        try:
            picker = self.driver.find_elements_by_css_selector('.left-wrapper')[-1].find_elements_by_class_name('date-panel')[idx]
            picker.click()
            print('已经点击', label)
        except Exception as e:
            print('选择失败', label)
            picker = self.driver.find_elements_by_css_selector('.left-wrapper')[-2].find_elements_by_class_name('date-panel')[idx]
            picker.click()

        self.initiate_ranger()
        year, month, day = date.strip(' ').split('-')
        if month < '10':
            month = month.strip('0')
        if day < '10':
            day = day.strip('0')
        year = int(year)
        day = int(day)
        month = int(month)
        count = 0
        cury = int(self.ranger['cury'].text.split(' ')[0].strip())
        while cury != year and count < 50:
            if cury > year:
                self.ranger['ynn'].click()
            else:
                self.ranger['ypp'].click()
            count += 1
            cury = int(self.ranger['cury'].text.split(' ')[0].strip())
            if count == 15:
                print('set year failed...')
        # print('set year ok')
        count = 0
        curm = int(self.ranger['curm'].text.split(' ')[0].strip())
        while curm != month and count < 15:
            if curm > month:
                self.ranger['mnn'].click()
            else:
                self.ranger['mpp'].click()
            count += 1
            curm = int(self.ranger['curm'].text.split(' ')[0].strip())
            if count == 15:
                print('set month failed...')
        # print('set month ok')
        self.refresh_ranger()
        self.ranger['days'][int(day)-1].click()
        # print('set day ok')

    def quit(self):
        self.driver.close()


@click.group()
def cli():
    """
    有一定概率出现爬虫失败,为页面元素无法定位导致,暂未找到原因,发生问题后请重跑一次,一般都能自行恢复
    """
    pass


@cli.command()
@click.option('-w','--kws', help='待查询关键词, 不得超过五个,逗号分开')
@click.option('-b','--date1', required=True, help='起始日期,示例2018-08-19')
@click.option('-e','--date2', required=True, help='结束日期,示例2018-09-10')
@click.option('-t','--terminal', required=True, default='both', help='终端类型: pc/mobile/both, 默认both')
@click.option('-o','--file_path', required=True, help='结果文件路径,只能是xlsx格式')
def crawl(kws, date1, date2, file_path, terminal):
    if kws is None:
        kws = raw_kws
    start = time.time()
    crawler = Crawler()

    date_groups = split_groups(date1, date2)
    click.echo(f'basic info <kws:{kws}>, <date:{date1}-{date2}>')

    kws = kws.split(',')
    valid, err_kws = crawler.check_validation(kws)
    if not valid:
        if len(err_kws) > 0:
            kws = [k for k in kws if k not in err_kws]
            if len(kws) == 0:
                click.echo(f'下列关键词未被百度指数收录: {err_kws}')
                return
            else:
                crawler.check_validation(kws)
        else:
            click.echo('页面加载失败')
            return

    time.sleep(4)
    df = pd.DataFrame()
    state = crawler.set_terminal(terminal)
    if not state:
        click.echo('终端选择错误, 退出')
        return
    for date1, date2 in date_groups:
        try:
            click.echo(f'时间段{date1}-{date2}的数据')
            state = crawler.set_date_range(date1, date2)

            if state:
                click.echo(f'正在解析时间段{date1}-{date2}的数据')
                df = pd.concat([df, crawler.fetch_all_data(kws)])
            elif not state1:
                click.echo(f'时间设置错误, 跳过')

        except Exception as e:
            click.echo(f'error happend: {date1}-{date2}, {e}')


    df = df.drop_duplicates(['date'])
    df.to_excel(file_path, index=False, encoding='utf-8')
    crawler.quit()
    click.echo(f'done, total cost time: {time.time()-start}')
    if len(err_kws) > 0:
        click.echo(f'下列关键词未被百度指数收录: {err_kws}')
    return df


def split_groups(date1, date2):
    start = arrow.get(date1)
    d2 = arrow.get(date2)
    if d2 > arrow.now():
        d2 = arrow.now()
    ret = []

    while start < d2:
        cur = start.shift(days=363)
        if cur > d2:
            cur = d2
        ret.append((start.shift(days=-1).format('YYYY-MM-DD'), cur.format('YYYY-MM-DD')))
        start = cur
    print(f'时间片是{ret}')
    return ret


if __name__ == '__main__':
    cli()
