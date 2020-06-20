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