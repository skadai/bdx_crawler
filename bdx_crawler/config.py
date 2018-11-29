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
raw_cookie = "BAIDUID=36DC40E114247973A02700133D73A5D4:FG=1; BIDUPSID=36DC40E114247973A02700133D73A5D4; PSTM=1541396701; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSFRCVID=IWFOJeC62AOj9Sc7UvViUGuGomK5CqJTH6aosmp7AZ1ZOgsSb5sREG0Pqf8g0Ku-fVt7ogKK3gOTH4PF_2uxOjjg8UtVJeC6EG0P3J; H_BDCLCKID_SF=tbPt_Kt2JDvqKROkq4cE-t4hMMoXetJyaR3A-hQvWJ5TMCoqXPCB0PJW3qjpalQxbmvyWlka0-jkShPC-tn5hJOWLJCDXfRM-a7a_4O43l02V-jIe-t2ynQDbRjJt-RMW20e0h7mWIbmsxA45J7cM4IseboJLfT-0bc4KKJxthF0HPonHjKbe53b3f; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1541696953,1541996173,1543226955; bdindexid=h9mr4evaetp56h1bu0b2gljat2; CHKFORREG=077543553499a629b852d38a991c69a4; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; PSINO=6; H_PS_PSSID=27774_1434_21081_20719; BDUSS=lyUGZJRnFsU3gzR1JvYjJ2S3c0YmJHZkxFTWFRaFJYb3RCLVM1Um1oNFFBU1pjQVFBQUFBJCQAAAAAAAAAAAEAAACNUrjnc2thZGFpNjY2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABB0~lsQdP5bNz; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1543402522"
temp = os.path.join(HOME_DIR, 'temp')

raw_config = dict(
    cookie=raw_cookie,
    temp_path=os.getenv('BDX_TEMP', temp)
)

province_dict = dict(
    group1=['安徽','澳门','北京','重庆','福建','广东','广西','甘肃','贵州'],
    group2=['河北','黑龙江','河南','湖南','湖北','海南','吉林','江苏','江西'],
    group3=['辽宁','内蒙古','宁夏','青海','上海','四川','山东','山西','陕西'],
    group4=['天津','台湾','西藏','香港','新疆','云南','浙江']
)
