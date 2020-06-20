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
            self.db.run(self.db.add(ip+':'+port))