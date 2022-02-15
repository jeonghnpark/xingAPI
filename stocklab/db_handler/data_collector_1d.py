from mongodb_handler import MongoDBHandler
from stocklab.agent.ebest import EBest
from datetime import datetime
import time

mongodb = MongoDBHandler()
ebest = EBest("DEMO")
ebest.login()


def collect_code_list():
    result = ebest.get_code_list("ALL")
    mongodb.delete_items(condition={}, db_name='stocklab', collection_name='code_info')
    mongodb.insert_items(datas=result, db_name='stocklab', collection_name='code_info')


def collect_stock_info():
    code_list = mongodb.find_items({}, 'stocklab', "code_info")

    target_code = set(item['shcode'] for item in code_list)
    # 오늘 price가 있는 종목은 제외
    today = datetime.today().strftime("%Y%m%d")
    collect_list = mongodb.find_items({'date': today}, 'stocklab', 'price_info').distinct('code')
    for col in collect_list:
        target_code.remove(col)

    for code in target_code:
        result_price = ebest.get_stock_price_by_code(code, 1, "1")
        time.sleep(1)
        if len(result_price) > 0:
            mongodb.insert_items(result_price, 'stocklab', "price_info")

    # target_code = set([item["단축코드"] for item in code_list])


if __name__ == '__main__':
    # collect_code_list()
    collect_stock_info()

# collect_code_list()
# cursor = mongodb.find_items(condition={}, db_name='stocklab', collection_name='code_info')
# for doc in cursor:
#     print(doc)

# codelist = ebest.get_code_list("ALL")
# codelist2 = mongodb.find_items({}, 'stocklab', 'code_info')
# target_code = set(item['shcode'] for item in codelist2)

# today = datetime.today()
# print(today)

# today = datetime.today().strftime('%Y%m%d')
# collect_list = mongodb.find_items({'날짜': today}, 'stocklab', 'price_info').distinct('code')
# target_collect_list = set(item['shcode'] for item in collect_list)
#
# # print([item])
# i = 3
