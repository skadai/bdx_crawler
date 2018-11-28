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

# 这个cookie仅用于测试, cookie可能失效, 你需要替换自己的有效的cookie
raw_cookie = "<your baidu cookie>"
temp = os.path.join(HOME_DIR, 'temp')

raw_config = dict(
    cookie=raw_cookie,
    temp_path=os.getenv('BDX_TEMP', temp)
)
