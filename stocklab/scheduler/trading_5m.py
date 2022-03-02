import time
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from stocklab.agent.ebest import EBest

from stocklab.db_handler.mongodb_handler import MongoDBHandler

from multiprocessing import Process

#demo mode
ebest_demo=EBest("DEMO")
ebest_demo.login()
mongo=MongoDBHandler()



def check_buy_order(code):
    """매수 주문 완료 여부 체크"""
    order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_ordered"}]},
                                       "stocklab_demo", "order"))
    for order in order_list:
        time.sleep(1)
        code=order['code'] #order['shcode']?
        order_no=order['buy_order']['ordno']
        order_cnt=order['buy_order']['qty']
        check_result=ebest_demo.order_check(order_no)
        print("'check buy order result", check_result)
        result_cnt=check_result['traded_amt']
        if order_cnt==result_cnt:
            mongo.update_item({"order_no":order_no},{"$set":{"buy_completed":check_result, "status": "buy_completed"}},
                              "stocklab_demo", "order")

            print("buy_completed", check_result)

    return len(order_list)


def check_buy_completed_order(code):
    """매수 체결 여부 체크"""
    buy_completed_order_list=list(mongo.find_items({"$and":[{"code":code},{"status":"buy_completed"}]},
                                                   "stocklab_demo", "order"))

def trading_scenario(code_list):
    for code in code_list:
        time.sleep(1)
        print(code)

        result = ebest_demo.get_current_price_by_code(code)
        current_price = result[0]['price']
        print(f"current price of {code} is ", current_price)
        """check buy order"""
        buy_order_cnt = check_buy_order(code)
        check_buy_completed_order(code)

        if buy_order_cnt==0:
            """보유 종목 없을시 무조건(as a strategy) 신규매수 """
            order=ebest_demo.order_stock(code,"2", current_price,"2","00")
            print("order_stock", order)
            order_doc=order[0]
            # order_doc
            # result: dict
            #     OrdNo: long
            #     OrdTime: str
            #     OrdMktCode: str , 주문시장코드
            #     OrdPtnCode: str, 주문유형코드
            #     ShtnIsuNo: str, 단축종목코드
            #     MgempNo: str,  관리사원번호 -> 삭제
            #     OrdAmt: long, 주문금액
            #     SpotOrdQty: long, 실주문수량
            #     IsuNm: str, 종목명

            mongo.insert_item({"buy_order":order_doc, "code":code, "status": "buy_ordered"},
                              "stocklab_demo", "order")

        check_sell_order(code)


def run_process_trading_scenario(code_list):
    p = Process(target=trading_scenario, args=(code_list,))
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

    #trigger="interval", minutes=1 인 경우 프로그램 시작후 1분간격
    #trigger="cron", minute="05" 는 매시 5분, 10분 에 실행됨
    scheduler.add_job(func=run_process_trading_scenario,
                      trigger="interval", seconds=10, id='demo',
                      kwargs={"code_list": code_list})


    scheduler.start()

    while True:
        print("wait... ", datetime.now())
        time.sleep(1)
