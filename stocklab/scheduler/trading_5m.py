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

DB_NAME="stocklab_demo"


def check_sell_order(code):
    """매도주문이 체결되었는지 체크 후 체결시에.
    상태변경: 'status':'sell_ordered'-> 'sell_completed'
    매도주문필드 추가: 'sell_completed_doc':check_result
    """
    sell_order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "sell_ordered"}]},
                                            DB_NAME, "order"))

    for order in sell_order_list:
        time.sleep(1)
        code = order['code']
        order_no = order['sell_order_doc']["OrdNo"]
        order_cnt = order['sell_order_doc']['SpotOrdQty']
        check_result = ebest_demo.order_check(order_no)  # 매도주문쿼리
        print("check sell order ", check_result)
        result_cnt = check_result['cheqty']
        if order_cnt == result_cnt:  # 주문수량과 체결수량이 같으면
            mongo.update_item({'sell_order_doc.OrdNo': order_no},
                              {"$set": {"sell_completed_doc": check_result, "status": "sell_completed"}},
                              DB_NAME, 'order')
            print("sell completed", check_result)

    return len(sell_order_list)


def check_buy_completed_order(code):
    """매수 완료된 주문은 매도 주문
    """
    buy_completed_order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_completed"}]},
                                                     DB_NAME, "order"))

    #매도 주문
    for buy_completed_order in buy_completed_order_list:
        buy_price=buy_completed_order['buy_completed_doc']['price'] # 체결가격
        buy_order_no=buy_completed_order['buy_completed_doc']['ordno']
        tick_size=ebest_demo.get_tick_size(int(buy_price))
        print('tick size', tick_size)
        sell_price=int(buy_price)+tick_size*10
        sell_order=ebest_demo.order_stock(code,"2", str(sell_price), "1", "00")
        print("order_stock", sell_order)
        mongo.update_item({"buy_completed_doc.ordno":buy_order_no},
                          {"$set":{"sell_order_doc":sell_order[0], "status": "sell_ordered"}},
                          DB_NAME,"order")  #TODO : sell_order[0] why?


def check_buy_order(code):
    """ DB에서 매수가 들어간 목록에 대해서
    ebest에 쿼리하여 체결여부를 확인한후 체결되었다면
    DB의 상태를 'status': 'buy_completed' 로변경하고,  'buy_completed_doc' 필드기록"""
    order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_ordered"}]},
                                       DB_NAME, "order"))
    for order in order_list: #
        time.sleep(1)
        code = order['code']  # order['shcode']?
        order_no = order['buy_order_doc']['OrdNo']
        order_cnt = order['buy_order_doc']['SpotOrdQty'] #실주문수량
        check_result = ebest_demo.order_check(order_no) #쿼리하여 체결/미체결여부 확인

        print("'check buy order result", check_result)
        result_cnt = check_result['cheqty'] #체결수량
        if order_cnt == result_cnt:
            mongo.update_item({"buy_order_doc.OrdNo": order_no},
                              {"$set": {"buy_completed_doc": check_result, "status": "buy_completed"}},
                              DB_NAME, "order")

            print("buy_completed", check_result)


    return len(order_list)


def trading_scenario(code_list):
    for code in code_list:
        time.sleep(1)
        print(code)

        result = ebest_demo.get_current_price_by_code(code)
        current_price = result[0]['price']
        print(f"current price of {result[0]['hname']} is ", current_price)

        """
        Run 1.무조건 매수
        Run 2. 1)매수 체결되었으면 buy_completed 로 변경, 매도 주문, 매도주문 체결 여부 체크
                2)매수 체결이 안되었으면 패스
        Run3.  전단계에서 매수체결이 되었으면 buy_ordered가 없으므로 신규매수
        """
        buy_order_cnt = check_buy_order(code)   #최초 0리턴
                                                #최초 이후에는 'status':'buy_ordered' 인 것의 개수를 리턴
                                                #DB 매수 주문항목에서 체결여부확인후 체결되었으면,
                                                #상태변경 'status':'buy_orderd' -> 'buy_completed'
                                                #매수주문 필드 추가: "buy_completed":check_result
                                                #주의! buy_completed로 바뀌기 전의 개수를 리턴
                                                #그렇게하지 않으면 buy_completed로 바뀌면서 바로 신규 매수 들어감

        check_buy_completed_order(code) #'status':'buy_completed' 인 경우 매도 주문내고
                                        #'status': 'sell_ordered' 로 변경

        if buy_order_cnt == 0:  #'status':buy_ordered 가 없을시 (as a strategy) 신규매수
            order = ebest_demo.order_stock(code, "2", current_price, "2", "00")
            print("order_stock", order)
            order_doc = order[0]
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

            mongo.insert_item({"buy_order_doc": order_doc, "code": code, "status": "buy_ordered"},
                              DB_NAME, "order")

        check_sell_order(code)  #"status": "sell_ordered" 항목에 대해서 체결되었는지 체크 후 체결시에.
                                #상태변경: 'status':'sell_ordered'-> 'sell_completed'
                                #매도주문필드 추가: 'sell_completed_doc':check_result


def run_process_trading_scenario(code_list):
    p = Process(target=trading_scenario, args=(code_list,))
    p.start()
    p.join()
    print("run process join")


# ebest_demo = EBest("DEMO")  # should be global since each process calls it
# ebest_demo.login()
# mongo = MongoDBHandler()

if __name__ == "__main__":


    """주문내역 DB삭제하기"""
    ordered_list=list(mongo.find_items({},DB_NAME,'order'))
    if ordered_list is not None:
        mongo.delete_items({},DB_NAME, 'order')
    """삭제확인"""
    ordered_list = list(mongo.find_items({}, DB_NAME, 'order'))
    assert len(ordered_list)==0


    scheduler = BackgroundScheduler()
    day = datetime.now() - timedelta(days=4)
    today = day.strftime("%Y%m%d")
    code_list = ["005930"]

    print('today', today)

    #trigger="interval", minutes=1 인 경우 프로그램 시작후 1분간격
    #trigger="cron", minute="05" 는 매시 5분, 10분 에 실행됨
    # scheduler.add_job(func=run_process_trading_scenario,
    #                   trigger="interval", minutes=5, id='demo',
    #                   kwargs={"code_list": code_list})

    scheduler.add_job(func=run_process_trading_scenario,
                      trigger="cron", year='2022', month='3', day='4', hour="15", minute="1", id='demo',
                      kwargs={"code_list": code_list})

    scheduler.start()

    while True:
        print("wait... ", datetime.now())
        time.sleep(1)
