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