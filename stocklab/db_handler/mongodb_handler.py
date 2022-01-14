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
        return self._client[db_name][collection_name].find_one(condition, {"_id": False})  # id는 빼고 리턴

    def find_items(self, condition=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            condition = {}  # no condition-> all data in db_collection
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, db_collection")
        return self._client[db_name][db_collection].find(condition, {"_id": False}, no_cursor_timeout=True,
                                                         cursor_type=CursorType.EXHAUST)

    def delete_items(self, condition=None, db_name=None, db_collection=None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("need condition as a dict")

        if db_name is None or db_collection is None:
            raise Exception("need db_name, db_collection")

        return self._client[db_name][db_collection].delete_many(condition)

    def update_items(self, condition=None, update_value=None, db_name=None, db_collection=None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("need condition as a dict")

        if db_name is None or db_collection is None:
            raise Exception("need db_name, db_collection")

        return self._client[db_name][db_collection].update_many(filter=condition, update=update_value)

    def update_item(self, condition=None, update_value=None, db_name=None, db_collection=None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("need condition as a dict")

        if db_name is None or db_collection is None:
            raise Exception("need db_name, db_collection")

        return self._client[db_name][db_collection].update_one(filter=condition, update=update_value)

    def aggregate(self, pipeline=None, db_name=None, collection_name=None):
        """
        MongoDB의 aggregation 작업을 위한 메소드
        :param pipeline:list: 갱신조건을 dict list로 받는다. [{},{},]
        :param db_name:
        :param collection_name:
        :return: CommandCursor:obj: PyMongo의
        """

        if pipeline is None or not isinstance(pipeline, list):
            raise Exception("need condition as a dict")
        if db_name is None or db_collection is None:
            raise Exception("need db_name, db_collection")
        return self._client[db_name][collection_name].aggregate(pipeline)

    def text_search(self, text=None, db_name=None, db_collection=None):
        if text is None or not isinstance(text, str):
            raise Exception("need text str")

        if db_name is None or db_collection is None:
            raise Exception("need db_name, db_collection")

        return self._client[db_name][db_collection].find({"$text": {"$sear"}})


if __name__ == "__main__":
    db = MongoDBHandler()
