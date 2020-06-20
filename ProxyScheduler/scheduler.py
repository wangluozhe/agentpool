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