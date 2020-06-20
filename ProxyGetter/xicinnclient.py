import requests
from lxml import etree
import time
from ProxyDatabase.dbclient import DBClient
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class XiCiNNClient(object):

    def __init__(self,pages=4000):
        self.headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'www.xicidaili.com',
        'Referer': 'https://www.xicidaili.com/nn/2',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
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
        url = 'https://www.xicidaili.com/nn/{page}'.format(page=str(page))
        self.headers['Referer'] = url
        response = requests.get(url,headers=self.headers)
        text = response.text
        html = etree.HTML(text)
        trs = html.xpath('//table[@id="ip_list"]/tr')
        for tr in trs:
            try:
                ip = tr.xpath('./td[2]/text()')[0]
                port = tr.xpath('./td[3]/text()')[0]
                self.db.run(self.db.add(ip+':'+port))
            except Exception as e:
                continue