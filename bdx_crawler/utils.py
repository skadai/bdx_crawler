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
import time
import math
import html

import requests
import arrow
import pandas as pd
import urllib
import click
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from .config import raw_config


class Crawler:
    def __init__(self, debug=False):
        if debug:
            self.driver = webdriver.Chrome()
        else:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.base_url = "http://index.baidu.com/v2/main/index.html#/trend/{}?words={}"
        self.max_try = 3
        self.base_cookie = {}
        self.ranger = {}
        self.flag = 0
        self.confirm = 1
        self.init_driver()

    def init_driver(self):
        # 先进入指定的网页, 然后才能替换cookie
        self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
        self.driver.get('http://index.baidu.com')
        for item in raw_config['cookie'].split(';'):
            kv = item.strip().split('=')
            self.base_cookie[kv[0]] = '='.join(kv[1:])
        self.driver.delete_all_cookies()
        for k, v in self.base_cookie.items():
            self.driver.add_cookie({'name': k, 'value': v})

    def make_url(self, keywords):
        words = []
        for kw in keywords:
            words.append(urllib.parse.quote(kw.encode('utf-8')))
        url = self.base_url.format(words[0], ','.join(words))
        return url

    @staticmethod
    def filter_valid_kws(kws):
        url = "https://index.baidu.com/api/AddWordApi/checkWordsExists?word={}"
        undefined_kws = []

        # 滤掉法语, 去重, 删除中文点符号
        clear_kws = set()
        for k in kws:
            if set('àâäèéêëîïôœùûüÿçÀÂÄÈÉÊËÎÏÔŒÙÛÜŸÇ') & set(k) == set():
                clear_kws.add(k.strip().lower().replace('•', '').replace('·', ''))
            else:
                undefined_kws.append(k)
        kws = list(clear_kws)

        # 百度合法性检查接口只能传入5个词, 但是可以通过+把多个词连起来当成一个词, 这里一次传入10词进行查询
        kw_group = [kws[i:i+10] for i in range(0, len(kws), 10)]
        kw_group_plus = map(lambda x: ['+'.join(x[i:i+2]) for i in range(0, len(x), 2)], kw_group)
        count = 0
        for kw in kw_group_plus:
            format_kw = ','.join(kw).encode('utf-8')
            while count < 3:
                try:
                    r = requests.get(url.format(urllib.parse.quote(format_kw)), headers=dict(Cookie=raw_config['cookie']))
                    ret = r.json()
                    # print(ret)
                    if len(ret['data']['result']) > 0:
                        unescaped_w = html.unescape(ret['data']['result'][0]['word'])
                        click.echo(f'检查到非法词 {unescaped_w}')
                        undefined_kws.extend(unescaped_w.split(','))
                    break
                except Exception as e:
                    click.echo(f'合法性检查出错 {ret}')
                    count += 1
        valid_kws = list(set(kws).difference(undefined_kws))
        return valid_kws, undefined_kws

    def check_validation(self, kws):
        if len(kws) == 0:
            return False, []
        url = self.make_url(kws)
        # click.echo(url)
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
                # click.echo(f'还没有加载出来页面...{e}')
                self.driver.get(url)
                time.sleep(3)
            count += 1

        if len(charts) == 0:
            click.echo('加载页面失败....')
            return False, []

        count = 0
        while count < self.max_try:
            try:
                text = self.driver.find_element_by_css_selector('.words').text
                return False, text.split(',')
            except Exception as e:
                # click.echo(f'未检出异常 {count+1}次')
                pass
            count += 1
        return True, []

    def fetch_all_data(self, kws):
        # 设置扫描步频
        date_picker = self.driver.find_element_by_class_name('index-date-range-picker')
        start, end = date_picker.text.split('~')
        # click.echo(f'start:{start}, end: {end}')
        start = start.strip()
        end = end.strip()
        xoyelement = self.driver.find_elements_by_css_selector('.index-trend-chart')[0]
        x, y = -1, 250

        days = (arrow.get(end)-arrow.get(start)).days
        delta = math.ceil(365 / days * 2)
        # click.echo(f'当前的天数{days}是使用的扫描步频是,{delta}')
        datas = []

        err_count = 0
        while 1:
            # 当连续错误次数过多, 停止循环
            if x > 2000 or err_count > 30:
                click.echo(f'循环次数过多, 跳出<x: {x}>')
                break

            ret = self.move_cursor(xoyelement, x, y)
            if len(ret) > 2:
                # click.echo(f'解析出的ret: {ret}')
                err_count = 0
                ret[0] = ret[0].split(' ')[0]
                if len(datas) == 0:
                    datas.append(ret[0::2])
                    # click.echo(f'add, {ret[0::2]}, ---x-cord {x}')
                    x += delta
                # 当获取到最后一天,终止循环
                elif ret[0].startswith(end):
                    datas.append(ret[0::2])
                    click.echo(f'已拿到最终数据 {ret[0::2]},跳出: --x-cord {x}')
                    break
                # 当接近最后一天, 减少步频
                elif arrow.get(datas[-1][0]).shift(days=1) == arrow.get(end):
                    # click.echo(f'快到终点，调整delta: {ret[0]}')
                    x += delta/5
                # 当日期连续, 录入; 日期不连续, 回退
                else:
                    cur_date = arrow.get(ret[0])
                    last_date = arrow.get(datas[-1][0])
                    if cur_date > last_date.shift(days=1):
                        x -= delta*3/4
                        # click.echo(f'日期不连续{ret[0]}, 需后退... --x-cord {x}')
                    elif cur_date == last_date.shift(days=1):
                        datas.append(ret[0::2])
                        # click.echo(f'add, {ret[0::2]}, ---x-cord {x}')
                        if cur_date.shift(days=1) == arrow.get(end):
                            x += delta/8
                        else:
                            x += delta
                    else:
                        x += delta
            else:
                # click.echo(f'没有解析出日期,进行下一次扫描')
                err_count += 1
                x += delta

        df = pd.DataFrame(datas, columns=['date']+kws)
        # click.echo(f'图中的天数是{days},已抓取{len(df)}')
        return df

    def initiate_ranger(self):
        ynn, cury, ypp = self.driver.find_elements_by_class_name('veui-calendar-left')[self.flag].find_elements_by_css_selector('button')
        if cury.text == '' and self.flag > 1:
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
        # print('ranger解析年结果',cury.text)

    def refresh_ranger(self):
        self.ranger['days'] = self.driver.find_elements_by_css_selector('.veui-calendar-body')[self.flag].find_elements_by_css_selector('.veui-calendar-day')

    def set_terminal(self, terminal):
        if terminal == 'both':
            return True
        if terminal == 'mobile':
            idx = 2
        else:
            idx = 1
        try:
            self.driver.find_elements_by_class_name('index-dropdown-list')[1].click()
        except Exception as e:
            return False
        # click.echo('正在打开终端选项,请稍候...')
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
        # click.echo('正在打开时间选项,请稍候...')
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
        # click.echo(f'now we set date....{label},{date}')
        idx = 0 if label == 'begin' else 1
        self.flag = idx + 2
        try:
            picker = self.driver.find_elements_by_css_selector('.left-wrapper')[-1].find_elements_by_class_name('date-panel')[idx]
            picker.click()
            # print('已经点击', label)
        except Exception as e:
            # print('选择失败', label)
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


def split_groups(start, d2):
    if d2 > arrow.now():
        d2 = arrow.now()
    ret = []

    while start < d2:
        cur = start.shift(days=363)
        if cur > d2:
            cur = d2
        ret.append((start.shift(days=-1).format('YYYY-MM-DD'), cur.format('YYYY-MM-DD')))
        start = cur
    # print(f'时间片是{ret}')
    return ret


def load_config(file_path):
    bdx_config = {}
    with open(file_path, 'r', encoding='utf-8') as c:
        config = c.read().splitlines()

    for item in config:
        if not item.startswith('#') and '=' in item:
            kv = item.split('=')
            bdx_config[kv[0].strip()] = '='.join(kv[1:]).strip()
    # print(bdx_config)
    return bdx_config
