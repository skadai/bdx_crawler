# -*- coding: utf-8 -*-

# @File    : setup.py
# @Date    : 2018-11-28
# @Author  : skym

# -*- coding: utf-8 -*-
from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


def load_require():
    with open('requirements.txt', 'r') as f:
        return f.read().split('\n')


setup(name='bdx_crawler',
      version='0.1',
      description='simple baidu index crawler',
      long_description=readme(),
      keywords='baidu_index',
      author='skchang',
      author_email='changshuangkai@yimian.com.cn',
      packages=['bdx_crawler'],
      install_requires=load_require(),
      include_package_data=True,
      entry_points={
            'console_scripts': ['bdx=bdx_crawler.command_line:cli'],
      },
      zip_safe=False)
