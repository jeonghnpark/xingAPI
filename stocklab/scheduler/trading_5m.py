import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from stocklab.agent.ebest import EBest

from stocklab.db_handler.mongodb_handler import MongoDBHandler

from multiprocessing import Process


def check_buy_order(code):
    """senity check for buying order"""
    order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_ordered"}]},
                                       "stocklab_demo", "order"))


def trading_scenario(code_list):
    for code in code_list:
        time.sleep(1)
        print(code)

        result = ebest_demo.get_current_call_price_by_code(code)
        current_price = result[0]['price']
        print("current price", current_price)
        """check buy order"""
        buy_order_cnt = check_buy_order(code)


def run_process_trading_scenario(code_list):
    p = Process(target=trading_scenario, args=(code_list))
    p.start()
    p.join()
    print("run process join")


ebest_demo = EBest("DEMO")  # should be global since each process calls it
ebest_demo.login()
mongo = MongoDBHandler()

if __name__ == "__main__":

    scheduler = BackgroundScheduler()
    day = datetime.now() - timedelta(days=4)
    today = day.strftime("%Y%m%d")
    code_list = ['180640', "005930", "091990"]

    print('today', today)

    scheduler.add_job(func=run_process_trading_scenario,
                      trigger="interval", minutes=5, id='demo',
                      kwargs={"code_list": code_list})

    scheduler.start()

    while True:
        print("wait... ", datetime.now())
        time.sleep(1)
