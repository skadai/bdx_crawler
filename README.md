## bdx_crawler

> 百度指数爬虫

[TOC]

### 安装

- 根据操作系统下载chrome浏览器(70.0以上)和chrome驱动(70.0以上)，chrome驱动的下载地址是

  https://npm.taobao.org/mirrors/chromedriver/71.0.3578.33/

- 将chromedriver所在路径加入系统path变量，操作方法请自行百度

- **增加`BDX_TEMP`环境变量, 指定中间文件保存的路径**，操作方法自行百度

  >本模块使用selenium爬虫百度指数，需要光标在页面中移动进行解析，有一定概率遇到无法定位页面元素导致程序失败，此时如果保存了中间文件，则重新从失败位置继续抓取即可

- 安装本模块

  ```shell
  pip install git+https://git.coding.net/Brahms213/baidu.git
  ```

- 输入下面的命令 `bdx crawl --help`,如果能看到下面的程序帮助，则说明安装成功

  ```shell
  Usage: bdx crawl [OPTIONS]
  
  Options:
    -w, --kws TEXT           待查询关键词, 不得超过五个,逗号分开
    -b, --date1 TEXT         起始日期,示例2018-08-19
    -e, --date2 TEXT         结束日期,示例2018-09-10
    -t, --terminal TEXT      终端类型: pc/mobile/both, 默认both
    -o, --file_path TEXT     结果文件路径,只能是xlsx格式
    -n, --processes INTEGER  进程数目
    -d, --debug              是否为debug模式,默认关闭
    --help                   Show this message and exit.
  ```

### 使用

#### crawl 命令行参数设定爬虫参数

**帮助命令** `bdx crawl --help`

```shell
Usage: bdx crawl [OPTIONS]

Options:
  -w, --kws TEXT           待查询关键词, 不得超过五个,逗号分开
  -b, --date1 TEXT         起始日期,示例2018-08-19
  -e, --date2 TEXT         结束日期,示例2018-09-10
  -t, --terminal TEXT      终端类型: pc/mobile/both, 默认both
  -o, --file_path TEXT     结果文件路径,只能是xlsx格式
  -n, --processes INTEGER  进程数目
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



#### Crawlf  文件设定爬虫参数

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

```text
# crawl_sample
# 在等号后面设定你需要的参数, 不需要引号
# kws 多个关键词用, 分开, 注意是英文逗号
# date1/date2 日期的格式必须和样例保持一致,即YYYY-MM-DD

kws = 梅西,c罗
date1 = 2018-10-01
date2 = 2018-11-01
terminal = pc
file_path = best_player.xlsx
processes = 4
debug = 0
```

##### 输出

```
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

### 工作原理

1. 利用预制cookie跳过百度登录环节
2. 对关键词进行预检查，排除未收录的关键词
3. 5个关键词一组进行查询，selenium模拟点击设定关键词，时间范围，终端类型
4. selenium模拟移动光标解析不同日期的数据
5. 将不同关键词，不同时间范围的数据进行拼接，输出错误信息(如果有的话)

