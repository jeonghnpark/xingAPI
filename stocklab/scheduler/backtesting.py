
from multiprocessing import Process
import time
import datetime
# from datetime import datetime, timedelta
import inspect

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BlockingScheduler, BackgroundScheduler

from stocklab.agent.ebest import EBest
from stocklab.agent.data import Data
from stocklab.db_handler.mongodb_handler import MongoDBHandler

ebest_ace=EBest("ACE")
ebest_ace.login()

mongo=MongoDBHandler()
DB_NAME="stocklab_ace"


def run_process_trading_scenario(code_list, date):
    p=Process(target=run_trading_scenario, args=(code_list, date))
    p.start()
    p.join()
    print("run process join")

def run_trading_scenario(code_list, thedate):
    """주문내역 DB삭제하기"""
    ordered_list=list(mongo.find_items({},DB_NAME,'order'))
    if ordered_list is not None:
        mongo.delete_items({},DB_NAME, 'order')
    """삭제확인"""
    ordered_list = list(mongo.find_items({}, DB_NAME, 'order'))
    assert len(ordered_list)==0

    tick=0
    while tick<20:
        print(f'tick: {tick}')
        for code in code_list:
            current_price=ebest_ace.get_price_n_min_by_code(thedate, code,tick)
            print('current priced', current_price)
            time.sleep(1)
            buy_order_list=ebest_ace.order_stock(code,"2", current_price['open'], "2", "00") #return list of dict
            buy_order=buy_order_list[0] #type of buy_order : dict
            buy_order['amount']=2
            mongo.insert_item(buy_order,DB_NAME, 'order')
            sell_order_list=ebest_ace.order_stock(code, "1", current_price['close'], "1", '00')
            sell_order=sell_order_list[0]
            sell_order['amount']=1
            mongo.insert_item(sell_order, DB_NAME, 'order')
        tick+=1




if __name__ == '__main__':
    scheduler=BackgroundScheduler()
    code_list=['005930']
    theday = datetime.datetime.today() - datetime.timedelta(days=4)
    theday=theday.strftime("%Y%m%d")
    run_trading_scenario(['005930'], theday)


    # scheduler.add_job(func=run_process_trading_scenario, trigger='date', run_date=datetime.now(),
    #                   id='test', kwargs={"code_list":code_list, "date":day})
    # # run_process_trading_scenario
    # # run_process_trading_scenario
    # scheduler.start()

