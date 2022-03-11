import unittest

# from stocklab.agent.ebest import EBest
# from stocklab.db_handler.mongodb_handler import MongoDBHandler
from stocklab.scheduler.trading_5m import trading_scenario2
import inspect
import time

# ebest=EBest("DEMO")
# mongo=MongoDBHandler()

class TestTrading(unittest.TestCase):
    def setUp(self):
        pass
        # self.ebest=EBest("DEMO")
        # self.ebest.login()
        # self.mongo=MongoDBHandler()

    def tearDown(self):
        self.ebest.logout()

    def _test_unit_test(self):
        print("Hello Unit test")

    def test_strategy1(self):
        pass
if __name__ == '__main__':
    unittest.main()
