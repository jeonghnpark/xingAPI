import unittest, inspect

import pandas as pd

from stocklab.db_handler.mongodb_handler import MongoDBHandler

from pprint import pprint

import pymongo

from datetime import datetime
from stocklab.agent.ebest import EBest

import time

import pandas as pd


class MongoDBHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.mongodb_handler = MongoDBHandler()
        self.ebest = EBest("DEMO")
        self.ebest.login()

        # self.mongodb._client['stocklab_test']['corp_info'].drop()

    def _test_get_historical_price_from_db(self):
        res = self.mongodb_handler.find_items({'shcode': '005380'}, 'stocklab', 'price_info')
        for r in res[:10]:
            print(r)

    def _test_collect_stock_info(self):
        # 종목의 당일 종가를 업데이트
        code_list = self.mongodb_handler.find_items({}, 'stocklab', 'code_info').distinct('shcode')
        code_list = ['000020', '005930', '005380']
        today = datetime.today().strftime("%Y%m%d")

        print('before deletion')
        rec = self.mongodb_handler.find_items({'date': today}, 'stocklab', 'price_info')
        for r in rec:
            print(r)

        cusor = self.mongodb_handler.delete_items({'date': today}, 'stocklab',
                                                  'price_info')
        print('after delete')
        rec = self.mongodb_handler.find_items({'date': today}, 'stocklab', 'price_info')
        for r in rec:
            print(r)

        # 종가 받아서  db에 쓰기
        for cd in code_list:
            time.sleep(1)
            res = self.ebest.get_stock_price_by_code(cd, 1, 1)
            self.mongodb_handler.insert_items(res, 'stocklab', 'price_info')

        rec = self.mongodb_handler.find_items({'date': today}, 'stocklab', 'price_info')
        print('after update')
        for r in rec:
            print(r)

    def _test_list_collection_names(self):
        print(self.mongodb_handler.list_collection_names('stocklab'))

    def _test_list_database_names(self):
        # result_cursor = self.mongodb.find_items({}, 'stocklab', 'code_info')
        print(self.mongodb_handler.list_database_names())

        # cursor = db_stocklab.member.find()
        # print(list(cursor))

    def _test_find_item(self):
        # cursor = self.mongodb_handler.find_items({}, 'stocklab', 'code_info')
        cursor = self.mongodb_handler.find_items({}, 'stocklab', 'price_info')

        # print(cursor.get('expcode'))
        result = []
        for record in cursor:
            result.append(record)

        for l in result[:10]:
            print(l)
        # print(result)

        cursor = self.mongodb_handler.find_items({'shcode': '005930'}, 'stocklab', 'price_info')
        print("005930 case")
        for rec in cursor:
            print(rec)

    def test_delete_item(self):

        order_list = list(self.mongodb_handler.find_items({"status": "buy_ordered"},
                                           "stocklab_demo", "order"))
        if len(order_list) >0 :
            for rec in order_list:
                print(rec)
            delete_result=self.mongodb_handler.delete_items({"status":"buy_ordered"},"stocklab_demo", "order")

        else:
            print("no such items found.")


        # cursor=self.mongodb_handler.find_items({},'stocklab_demo', 'order')
        #
        # result = []
        # for record in cursor:
        #     result.append(record)
        #
        # for l in result[:10]:
        #     print(l)

        #
        # if len(list(cursor))==0:
        #     print('no such items found')
        # else:
        #     for rec in cursor:
        #         print(rec)


    def _test_test(self):
        print(3)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
