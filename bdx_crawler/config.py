# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    config
   Description :
   Author :       changsk
   date：          2018/11/27
-------------------------------------------------
   Change Activity:
                   2018/11/27:
-------------------------------------------------
"""
import os

HOME_DIR = os.path.expanduser('~')
ROOT_DIR = os.path.dirname(__file__)

# 这个cookie仅用于测试, cookie可能失效, 你需要替换自己的有效的cookie
with open(os.path.join(ROOT_DIR, 'secret'), 'r', encoding='utf-8') as c:
    cookie = c.read().strip('\n')

raw_config = dict(
    cookie=cookie,
    temp_path=os.getenv('BDX_TEMP', os.path.join(HOME_DIR, 'temp'))
)

province_dict = dict(
    group1=['安徽','澳门','北京','重庆','福建','广东','广西','甘肃','贵州'],
    group2=['河北','黑龙江','河南','湖南','湖北','海南','吉林','江苏','江西'],
    group3=['辽宁','内蒙古','宁夏','青海','上海','四川','山东','山西','陕西'],
    group4=['天津','台湾','西藏','香港','新疆','云南','浙江']
)
