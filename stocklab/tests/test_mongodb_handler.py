import unittest, inspect
from stocklab.db_handler.mongodb_handler import MongoDBHandler

from pprint import pprint

import pymongo


class MongoDBHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.mongodb_handler = MongoDBHandler()
        # self.mongodb._client['stocklab_test']['corp_info'].drop()

    def _test_list_collection_names(self):
        print(self.mongodb_handler.list_collection_names('stocklab'))

    def _test_list_database_names(self):
        # result_cursor = self.mongodb.find_items({}, 'stocklab', 'code_info')
        print(self.mongodb_handler.list_database_names())

        # cursor = db_stocklab.member.find()
        # print(list(cursor))

    def test_find_item(self):
        cursor = self.mongodb_handler.find_items({}, 'stocklab', 'code_info')
        # print(cursor.get('expcode'))
        for record in cursor:
            print(record)

    # for row in cursor:
    #     print(row)
    #
    # for row in cursor:
    #     print(row)

    # result = self.mongodb_handler.find_items({}, 'stocklab', 'price_info')
    # print(list(result))

    def _test_test(self):
        print(3)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
