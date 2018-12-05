## bdx_crawler

> 百度指数爬虫

[TOC]

### 安装

- 根据操作系统下载chrome浏览器**(70.0以上)**和chrome驱动**(70.0以上)**，chrome驱动的下载地址是

  https://npm.taobao.org/mirrors/chromedriver/71.0.3578.33/

  将chromedriver所在路径加入系统`PATH`变量，增加`BDX_TEMP`环境变量, 指定中间文件保存的路径，操作方法自行百度

  >本模块使用selenium爬虫百度指数，需要光标在页面中移动进行解析，有一定概率遇到无法定位页面元素导致程序失败，此时如果保存了中间文件，则重新从失败位置继续抓取即可

- 安装本模块

  ```shell
  pip install git+https://e.coding.net/yimian/bdx_crawler.git
  ```

  完成后输入命令 `bdx `,如果能看到下面的帮助打印，则说明安装成功

  ```shell
  Usage: bdx [OPTIONS] COMMAND [ARGS]...
  
    百度指数爬虫
  
  Options:
    --help  Show this message and exit.
  
  Commands:
    crawl   输入参数进行百度指数抓取
    crawlf  根据文件配置进行百度指数抓取, 文件配置参考crawl_sample
    repair  引导用户进行cookie重新设置
  ```

- **[很重要] 在使用前`务必`重置cookie为自己的百度合法cookie**

  > 预置的cookie 可能失效，此时需要人工设置合法的cookie。你可以手动复制百度的cookie到本模块安装目录下覆盖secret内容，也可以执行本命令。**secret文件内容请妥善保管!!!**

  ##### 输入

  - `bdx repair`浏览器打开百度登录页面, 输入合法的用户名密码登录成功后，命令行回车

  ##### 输出

  ```shell
  ➜  baidu git:(master) ✗ bdx repair
  请在【浏览器】页面登录你的百度账户, 登录成功后在【命令行】按任意键继续
  正在检查请稍候....
  恭喜你已经重新设置了cookie
  ```

  当看到命令行提示重置cookie成功后，即可继续进行正常的百度指数抓取操作

### 使用

#### crawl --命令行参数设定爬虫参数

**帮助命令** `bdx crawl --help`

```shell
Usage: bdx crawl [OPTIONS]

  输入参数进行百度指数抓取

Options:
  -w, --kws TEXT           待查询关键词, 英文逗号,分开  [required]
  -b, --date1 TEXT         起始日期,默认2018-01-01
  -e, --date2 TEXT         结束日期,示例2018-11-11
  -t, --terminal TEXT      终端类型: pc/mobile/both, 默认both
  -o, --file_path TEXT     结果文件路径, 只支持xlsx  [required]
  -n, --processes INTEGER  进程数目, 默认为4
  -p, --province TEXT      省份, 默认全国
  -d, --debug              是否为debug模式,默认关闭
  --help                   Show this message and exit.
```

#### 使用样例

> 爬取梅西和c罗在`2018年10月`的`手机`端百度指数，将结果保存到`best_player.xlsx`中

##### 输入

```shell
bdx crawl -w 梅西,c罗 -b 2018-10-01 -e 2018-11-01 -t mobile -o best_player.xlsx
```

##### 输出

```
basic info <kws:梅西,c罗>, <date:2018-10-01-2018-11-01>,<mobile>
共有2词需要爬取, 拆分为1个子任务
  [------------------------------------]    0%now we crawl for ['梅西', 'c罗']
正在解析 <['梅西', 'c罗']> 时间段 2018-09-30-2018-11-01 的数据
已拿到最终数据 ['2018-11-01', '  4,237', '  6,885'],跳出: --x-cord 1239.2749999999996
  [####################################]  100%
**************RESULT**************************
done, total cost time: 21.13531494140625
共32天数据,已抓取32天
所有日期都已经成功抓取了!
详细结果请前往best_player.xlsx查看
```



#### crawlf  --文件设定爬虫参数

**帮助命令** `bdx crawlf --help`

```shell
Usage: bdx crawlf [OPTIONS] CONFIG_FILE

  根据文件配置进行百度指数抓取, 文件配置参考crawl_sample

Options:
  --help  Show this message and exit.
```

#### 使用样例

> 爬取梅西和c罗在`2018年10月`的`PC`端百度指数，将结果保存到`best_player.xlsx`中

##### 输入

- `crawl_sample` 文件定义抓取的参数, 然后命令行`bdx crawlf crawl_sample`

```shell
# crawl_sample
# 在等号后面设定你需要的参数, 不需要引号
# kws 多个关键词用, 分开, 注意是英文逗号
# date1/date2 日期的格式必须和样例保持一致,即YYYY-MM-DD

kws = 梅西,c罗
date1 = 2018-10-01
date2 = 2018-11-01
terminal = pc
file_path = best_player.xlsx
province = 全国
processes = 4
debug = 0
```

##### 输出

```shell
basic info <kws:梅西,c罗>, <date:2018-10-01-2018-11-01>,<pc>
共有2词需要爬取, 拆分为1个子任务
  [------------------------------------]    0%now we crawl for ['c罗', '梅西']
正在解析 <['c罗', '梅西']> 时间段 2018-09-30-2018-11-01 的数据
已拿到最终数据 ['2018-11-01', '  2,430', '  1,945'],跳出: --x-cord 1239.2749999999996
  [####################################]  100%
**************RESULT**************************
done, total cost time: 20.8640398979187
共32天数据,已抓取32天
所有日期都已经成功抓取了!
详细结果请前往best_player.xlsx查看
```

### 工作过程

1. 利用预制cookie跳过百度登录环节
2. 对关键词进行预检查，排除未收录的关键词
3. 5个关键词一组进行查询，selenium模拟点击设定关键词，时间范围，终端类型
4. selenium模拟移动光标解析不同日期的数据
5. 将不同关键词，不同时间范围的数据进行拼接，输出错误信息(如果有的话)

### FAQ

####  1. 无法爬虫，最后打印一大堆日期...

开启` -d`选项，看浏览器页面卡死在哪一步了，**如果是显示百度登录页面，则说明cookie失效了，请使用repair命令更新**，其他情况请反馈问题

#### 2. 报错`No such file or directory: '/Users/**/temp/**.xlsx'`

你没有设置BDX_TEMP环境变量，请阅读 [安装](#安装) 一节  

#### 3. 报错 `selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH. Please see https://sites.google.com/a/chromium.org/chromedriver/home`

你没有将chromedriver添加到环境变量PATH，请阅读 [安装](#安装)一节  
