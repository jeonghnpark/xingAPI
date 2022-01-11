from pymongo import MongoClient
from pymongo.cursor import CursorType

import configparser


class MongoDBHandler:
    """pymongo wrapping class"""

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('D:\\dev\python\\xingAPI\\stocklab\\agent\\conf\\config.ini')
        host = config['MONGODB']['host']
        port = config['MONGODB']['port']
        self._client = MongoClient(host, int(port))

    def insert_item(self, data, db_name=None, collection_name=None):
        if not isinstance(data, dict):
            raise Exception("data type should be dict")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].insert_one(data).inserted_id

    def insert_items(self, datas, db_name=None, collection_name=None):
        if not isinstance(datas, list):
            raise Exception("datas type should be list")
        if db_name is None or collection_name is None:
            raise Exception("need to param db_name, collection name")

        return self._client[db_name][collection_name].insert_many(datas).inserted_ids

    def find_item(self, condition=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            condition = {}
        if db_name is None or collection_name is None:
            raise Exception("need to param db_name, collection name")
        return self._client[db_name][collection_name].find_one(condition, {"_id": False})


if __name__ == "__main__":
    db = MongoDBHandler()
