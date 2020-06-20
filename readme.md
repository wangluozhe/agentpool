### 代理介绍
爬虫工程师在爬取网页的过程中多多少少都会碰到各式各样的反爬虫手段，比如封IP、验证码、JS加密、数据加密等，这里最为常见的就是封IP了，当同一个IP访问网站的频率过高时，网站就会认为你是一个机器人而不是真人，这时候就会对此IP进行封禁处理，让你再次访问的时候出现验证码让你来识别，或者会给你一个提醒等，这个时候你的爬虫就爬不出来任何的数据了，此时要想破解封IP只能更换自己本机的IP或者进行代理操作，这就是代理的重要性，代理有免费代理和付费代理，免费代理非常不稳定，往往需要自己去维护。

### 代理池介绍
简单来说，代理池就是我们不想花钱买付费代理，而对某些网站的免费代理进行采集、检测、维护，使其能够正常使用的代理加入到代理池中，再以API的方式在提供给我们爬虫，这就是代理池的作用，当然付费代理也可以做代理池，但往往没人会这么做。

### 代理来源
|名称|地址|
|--|--|
|快代理|https://www.kuaidaili.com/free/|
|齐云免费代理|https://www.7yip.cn/free/|
|89免费代理|http://www.89ip.cn/|
|西刺代理|https://www.xicidaili.com/nn/、https://www.xicidaili.com/wt/|
|云代理|http://www.ip3366.net/free/?stype=1、http://www.ip3366.net/free/?stype=2|
|高可用全球免费代理|https://ip.jiangxianli.com/?page=1|

### 代理池规则
将采用代理分数制来对代理进行区分
代理分数制：
1.代理分数最高为100分，最低为0分，0分将进行删除
2.初次获取的代理分数均为10分
3.每次测试代理后，测试成功将设置为最高分，测试失败将扣除1分


### 代理池框架
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200523145554683.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQyMjc5MDc3,size_16,color_FFFFFF,t_70#pic_center)
`Proxy Scheduler(调度器)：`
用来启动(Start)各个模块的，使其可以正常运行工作。
`Proxy Getter(获取器)：`
定时从代理网站中获取(Fetch)免费代理，并将免费代理提交(PUT)给数据库。
`Proxy Tester(检测器)：`
定时从数据库中取出所有免费代理，并对免费代理进行检测刷新(Refresh)，根据结果来对免费代理进行操作(PUT/DELETE)。
`Porxy API(API接口)：`
提供给爬虫用户的一个接口，接口通过数据库来获取(GET)免费代理，返回给爬虫用户。
`Proxy Database(代理数据库)：`
实现数据库的一系列操作，将免费代理保存到数据库。
`Proxy Source(免费代理网站)：`
这个从网上找的各种代理网站，从里面获取到免费代理。
`Spider User(爬虫用户)：`
用户访问API链接，每次都是随机获取到一个免费代理。

### settings.py
```python
# Getter模块

# Getter模块处理请求的文件
GETTER_LISTS = ['KuaidailiClient','BaJiuIPClient','JiangXianLiClient','QiYunVipClient','XiCiNNClient','XiCiWTClient','YunDaiLi1Client','YunDaiLi2Client']

# Database模块
# 启用哪个数据库
DB_START = 'RedisClient'
# 数据库地址
DB_HOST = '127.0.0.1'
# 数据库端口
DB_PORT = 6379
# 数据库用户
DB_USERNAME = None
# 数据库密码
DB_PASSWORD = None
# 数据库库名
DB_DATABASE = 0
```

### 数据库模块实现
`db模块：`

主要是方便以后扩展其他数据库。

```python
import settings
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class DBClient():

    def __new__(cls, *args, **kwargs):
        db_start = settings.DB_START
        db_host = settings.DB_HOST
        db_port = settings.DB_PORT
        db_password = settings.DB_PASSWORD
        db_database = settings.DB_DATABASE
        if db_start == 'RedisClient':
            db = getattr(__import__('redisclient'),'RedisClient')(host=db_host,port=db_port,password=db_password,database=db_database)
        else:
            db_username = settings.DB_USERNAME
            db = getattr(__import__('redisclient'),'RedisClient')(host=db_host,port=db_port,username=db_username,password=db_password,database=db_database)
        return db
```

`redis模块：`

这里采用异步aioredis模块来实现数据插入。
```python
import asyncio
import aioredis
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

"""
:param MAX_SCORE: 分数最大值，100
:param MIN_SCORE: 分数最小值，0
:param INIT_SCORE: 分数初始值,10
:param REDIS_KEY: redis键名，默认为proxies
"""
MAX_SCORE = 100
MIN_SCORE = 0
INIT_SCORE = 10
REDIS_KEY = 'proxies'

class RedisClient(object):

    def __init__(self,host,port,password,database):
        """
        :param host: redis地址，默认为127.0.0.1
        :param port: redis端口，默认为6379
        :param password: redis密码，默认为None
        :param database: redis数据库，默认为0
        :param _redis: redis连接池对象，默认为None
        """
        self.host = host
        self.port = port
        self.password = password
        self.database = database
        self._redis = None
        self.__main()

    def __main(self):
        """
        启动异步redis操作
        :return: 启动异步redis
        """
        asyncio.run(self.__create_redis())

    def run(self,func):
        """
        执行异步函数
        :param func:异步函数
        :return:返回异步函数结果
        """
        return asyncio.run(func)

    async def __create_redis(self):
        """
        异步创建redis连接池，提供给下面其他函数进行操作
        :return: 创建redis连接池
        """
        if not self.host:
            self.host = '127.0.0.1'
        if not self.port:
            self.port = 6379
        if not self.database:
            self.database = 0
        if not self.password:
            self._redis = await aioredis.create_redis_pool('redis://{host}:{port}/{database}'.format(host=self.host,port=self.port,database=self.database))
        else:
            self._redis = await aioredis.create_redis_pool('redis://{host}:{port}'.format(host=self.host,port=self.port),db=self.database,password=self.password)

    async def __aadd(self,proxy,score=INIT_SCORE):
        """
        添加代理，设置初始分数
        :param proxy: 代理
        :param score: 分数
        :return: 添加代理
        """
        if not await self._redis.zscore(REDIS_KEY,proxy):
            return await self._redis.zadd(REDIS_KEY,score,proxy)

    def add(self,proxy):
        return self.__aadd(proxy)

    async def __arandom(self):
        """
        随机获取代理，首先获取最高分数的代理，如果最高分数不存在，则按照排名获取，否则提示异常
        :return:随机获取代理
        """
        result = await self._redis.zrangebyscore(REDIS_KEY,MAX_SCORE,MAX_SCORE)
        if len(result):
            return random.choice(result)
        else:
            result = await self._redis.zrevrange(REDIS_KEY,MIN_SCORE,MAX_SCORE)
            if len(result):
                return random.choice(result)
            else:
                return 'None'

    def random(self):
        return self.__arandom()

    async def __adecrease(self,proxy):
        """
        代理值减一分，分数小于最小分数则删除代理
        :param proxy: 代理
        :return: 修改后代理分数
        """
        score = await self._redis.zscore(REDIS_KEY,proxy)
        if score and score > MIN_SCORE:
            return await self._redis.zincrby(REDIS_KEY,-1,proxy)
        else:
            return await self._redis.zrem(REDIS_KEY,proxy)

    def decrease(self,proxy):
        return self.__adecrease(proxy)

    async def __aexists(self,proxy):
        """
        判断代理是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not await self._redis.zscore(REDIS_KEY,proxy) == None

    def exists(self,proxy):
        return self.__aexists(proxy)

    async def __amax(self,proxy):
        """
        设置代理分数为最高分
        :param proxy:  代理
        :return: 设置最高分
        """
        return await self._redis.zadd(REDIS_KEY,MAX_SCORE,proxy)

    def max(self,proxy):
        return self.__amax(proxy)

    async def __acount(self):
        """
        获取所有代理数量
        :return: 数量
        """
        return await self._redis.zcard(REDIS_KEY)

    def count(self):
        return self.__acount()

    async def __aall(self):
        """
        获取全部代理
        :return:全部代理列表
        """
        return await self._redis.zrangebyscore(REDIS_KEY,MIN_SCORE,MAX_SCORE)

    def all(self):
        return self.__aall()
```

### 获取器模块实现
`获取器：`

只需要将爬取过程定义为一个类（`注：一个文件一个类，文件名和类名必须相同，文件名为全小写，类名为大驼峰命名法`），将类名放置到`settings.py`文件的GETTER_LISTS列表中即可。

```python
import settings
import threading
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class GetterClient(object):

    def __init__(self):
        self.getter_lists = settings.GETTER_LISTS
        self.init_getter_client()
        print('定时爬虫开启')
        while True:
            self.timing_getter_client()
            # 每隔一天执行一次，相当于更新
            time.sleep(86400)

    # 获取初始代理
    def init_getter_client(self):
        for getter in self.getter_lists:
            t = threading.Thread(target=getattr(__import__(getter.lower()),getter))
            t.start()
            if getter == self.getter_lists[-1]:
                t.join()

    # 获取最新的十页代理
    def timing_getter_client(self):
        for getter in self.getter_lists:
            t = threading.Thread(target=getattr(__import__(getter.lower()),getter),args=(10,))
            t.start()
```
从`settings.py`文件中的`GETTER_LISTS`获取模块名，模块名被动态导入后使用线程运行。下面以快代理模块进行示例。

`快代理示例(kuaidailiclient.py)：`

仅需要实现爬取代理后进行插入数据即可。

```python
import requests
from lxml import etree
import time
from ProxyDatabase.dbclient import DBClient
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class KuaidailiClient(object):

    def __init__(self,pages=3000):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'channelid=0; sid=1591856578551410; _ga=GA1.2.1402864675.1591858326; _gid=GA1.2.618643665.1591858326; Hm_lvt_7ed65b1cc4b810e9fd37959c9bb51b31=1591858326; Hm_lpvt_7ed65b1cc4b810e9fd37959c9bb51b31=1591859117',
            'Host': 'www.kuaidaili.com',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        }
        self.pages = pages
        self.db = DBClient()
        for page in range(1,self.pages+1):
            self.fetch_proxy(page)
            time.sleep(5)

    def fetch_proxy(self,page):
        url = 'https://www.kuaidaili.com/free/inha/{page}/'.format(page=str(page))
        response = requests.get(url,headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        trs = html.xpath('//table[contains(@class,"table-bordered")]/tbody/tr')
        for tr in trs:
            ip = tr.xpath('./td[@data-title="IP"]/text()')[0]
            port = tr.xpath('./td[@data-title="PORT"]/text()')[0]
            # 插入操作
            self.db.run(self.db.add(ip+':'+port))
```

### 检测器模块实现
`检测器：`

由于代理数量太多，这里将使用的是异步aiohttp来进行检测操作，这样检测的速度是requests的几十倍。测试：使用代理访问百度页面，返回状态为200即为成功，其余均为失败，选择百度页面是因为其没有进行ip限制。

```python
from ProxyDatabase.dbclient import DBClient
import time
import aiohttp
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

TEST_URL = 'http://httpbin.org/get'
STATUS_CODE = [200]
BATCH_TEST_SIZE = 50
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.baidu.com',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
    }

class Tester(object):

    def __init__(self):
        self.redis = DBClient()
        while True:
            self.run()
            time.sleep(30)

    async def test_proxy(self,proxy):
        if isinstance(proxy,bytes):
            proxy = proxy.decode('utf-8')
        real_proxy = 'http://' + proxy
        print('测试中...',proxy)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=TEST_URL,proxy=real_proxy,headers=HEADERS,timeout=15) as response:
                    print(response.status)
                    if response.status in STATUS_CODE:
                        await self.redis.max(proxy)
                        print('代理可用',proxy)
                    else:
                        await self.redis.decrease(proxy)
                        print('请求响应码不合法',proxy)
            except BaseException as e:
                await self.redis.decrease(proxy)
                print('代理请求失败',proxy)

    def run(self):
        print('测试开始运行')
        try:
            proxies = self.redis.run(self.redis.all())
            for i in range(0,len(proxies),BATCH_TEST_SIZE):
                test_proxies = proxies[i:i+BATCH_TEST_SIZE]
                tasks = [self.test_proxy(proxy) for proxy in test_proxies]
                asyncio.run(asyncio.wait(tasks))
        except Exception as e:
            print('错误',e)
```

### API模块实现
`API：`

API的作用是用于自己或别人访问来获取代理IP用的。这里采用fastapi来做接口。

```python
from fastapi import FastAPI
import uvicorn
import aioredis
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()
db = None
MAX_SCORE = 100
MIN_SCORE = 0
INIT_SCORE = 10
REDIS_KEY = 'proxies'

@app.on_event('startup')
async def start_event():
    global db
    db = await aioredis.create_redis_pool('redis://{host}:{port}/{database}'.format(host='127.0.0.1',port=6379,database=0))

@app.get('/')
async def index():
    #提示操作
    return {
        'message':'欢迎使用LeeGene的个人代理池',
        '/random':'获取随机代理地址',
        '/count':'获取代理总数量'
    }

@app.get('/random')
async def randoms():
    result = await db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
    if len(result):
        return {
            'status':200,
            'proxy':random.choice(result)
        }
    else:
        result = await db.zrevrange(REDIS_KEY, MIN_SCORE, MAX_SCORE)
        if len(result):
            return {
                'status':200,
                'proxy':random.choice(result)
            }
        else:
            return {
                'status':200,
                'proxy':'None'
            }

@app.get('/count')
async def count():
    result = await db.zcount(REDIS_KEY,MAX_SCORE,MAX_SCORE)
    if result:
        return {
            'status':200,
            'count':result
        }
    else:
        return {
            'status':200,
            'count':0
        }

# 用于启动fastapi
def run(host='127.0.0.1',port=8000):
    uvicorn.run(app='api:app', host=host, port=port)
```

### 调度器模块实现
`调度器：`

调度器是用来启动`获取器`、`检测器`、`API`三个模块的，每个模块使用一个进程来进行启动，各自独立，互不影响，即使一个断开也不影响其他两个模块。

```python
from ProxyGetter.getterclient import GetterClient
from ProxyTester.tester import Tester
from ProxyAPI import api
from multiprocessing import Process
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class Scheduler(object):

    def scheduler_tester(self):
        print('测试器开始运行')
        tester = Tester()

    def scheduler_getter(self):
        print('获取器开始运行')
        getter = GetterClient()

    def scheduler_api(self):
        print('api接口开始运行')
        API = api.run()

    def run(self):
        tester_process = Process(target=self.scheduler_tester)
        tester_process.start()
        getter_process = Process(target=self.scheduler_getter)
        getter_process.start()
        api_process = Process(target=self.scheduler_api)
        api_process.start()
```

### agentpool.py
仅仅就是用来启动scheduler的，因为我的代理池名字叫agentpool，所以我就用agentpool这个名字来启动代理池，仅此而已。

```python
from ProxyScheduler.scheduler import Scheduler


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
```

### 总结
爬取速度、检测速度、数据库IO操作还是蛮快的，测试器和数据库都采用异步方式，获取器采用多线程方式，调度器采用多进程方式。