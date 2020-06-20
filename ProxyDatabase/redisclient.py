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