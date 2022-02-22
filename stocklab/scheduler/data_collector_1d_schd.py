import time
from datetime import datetime

import inspect
from multiprocessing import Process

from apscheduler.schedulers.background import BackgroundScheduler

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler


def collect_code_list():
    ebest = EBest("DEMO")
    mongodb = MongoDBHandler()
    ebest.login()

    result = ebest.get_code_list("ALL")
    mongodb.delete_items({}, 'stocklab', 'code_info')
    mongodb.insert_items(datas=result, db_name='stocklab', collection_name='code_info')


def collect_stock_info():
    ebest = EBest("DEMO")
    ebest.login()
    mongodb = MongoDBHandler()
    today = datetime.today().strftime("%Y%m%d")

    # code_list = mongodb.find_items({}, 'stocklab', 'code_info')
    lst_code_list = mongodb.find_items({}, 'stocklab', 'code_info').distinct('shcode')

    # target_code = set([item['shcode'] for item in code_list])
    # today = datetime.today().strftime("%Y%m%d")
    # list_removed_code = mongodb.find_items({"date": today}, db_name="stocklab", collection_name="price_info").distinct(
    #     "code")

    # 당일 가격이 있는 경우 레코드 삭제 - JH
    mongodb.delete_items({'date': today}, db_name='stocklab', collection_name='price_info')

    # for code in lst_code_list:

    # target_code.remove(code)

    for code in lst_code_list[:30]:
        time.sleep(1)
        result_price = ebest.get_stock_price_by_code(code, 1, 1)
        # res = self.ebest.get_stock_price_by_code(cd, 1, 1)
        if len(result_price) > 0:
            cursor = mongodb.insert_items(result_price, 'stocklab', 'price_info')
            if cursor is not None:
                print(f"{code} was recorded. ")


def run_process_collect_code_list():
    print(inspect.stack()[0][3])  # 현재 실행 모듈 명 출력
    p = Process(target=collect_code_list)
    p.start()
    p.join()


def run_process_collect_stock_info():
    print(inspect.stack()[0][3])
    p = Process(target=collect_stock_info)
    p.start()
    p.join()


if __name__ == "__main__":
    # scheduler = BackgroundScheduler()
    # # scheduler.add_job(func=run_process_collect_code_list, trigger='cron', day_of_week="mon-fri",
    # #                   hour="14", minute="27", id="1")
    # scheduler.add_job(func=run_process_collect_stock_info, trigger='cron', day_of_week='mon-fri',
    #                   hour="14", minute="30", id="2")
    # 
    # scheduler.start()
    # 
    # while True:
    #     print("running", datetime.now())
    #     time.sleep(5)
    # mongodb = MongoDBHandler()
    # today = datetime.today().strftime("%Y%m%d")
    #
    # res = mongodb.find_items({}, db_name='stocklab', collection_name='code_info')
    # for r in res:
    #     print(r)
    collect_stock_info()
