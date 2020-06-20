import requests
from lxml import etree
import time
from ProxyDatabase.dbclient import DBClient
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class QiYunVipClient(object):

    def __init__(self,pages=640):
        self.headers = {
            'authority': 'www.7yip.cn',
            'method': 'GET',
            'path': '/free/?action=china&page=1',
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
        }
        self.pages = pages
        self.db = DBClient()
        for page in range(1,self.pages+1):
            self.fetch_proxy(page)
            time.sleep(5)

    def fetch_proxy(self,page):
        url = 'https://www.7yip.cn/free/?action=china&page={page}'.format(page=str(page))
        self.headers['path'] = '/free/?action=china&page={page}'.format(page=str(page))
        response = requests.get(url,headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        trs = html.xpath('//table[contains(@class,"table-bordered")]/tbody/tr')
        for tr in trs:
            ip = tr.xpath('./td[@data-title="IP"]/text()')[0]
            port = tr.xpath('./td[@data-title="PORT"]/text()')[0]
            self.db.run(self.db.add(ip+':'+port))