import unittest
from stocklab.agent.ebest import EBest

import inspect
import time
import pandas as pd
import matplotlib.pyplot as plt

from stocklab.db_handler.mongodb_handler import MongoDBHandler
mongo=MongoDBHandler()
DB_NAME="stocklab_ace"

class TestEbest(unittest.TestCase):
    def setUp(self):
        self.ebest = EBest("ACE")
        self.ebest.login()

    def _test_get_current_call_price_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_current_call_price_by_code("005930")
        print(f"price of 005930 is {result[0]['price']}")

    def _test_get_code_list(self):
        print(inspect.stack()[0][3])  # test명
        all_result = self.ebest.get_code_list("ALL")
        assert all_result is not None
        kosdaq_result = self.ebest.get_code_list("KOSDAQ")
        assert kosdaq_result is not None
        # kospi_result = self.ebest.get_code_list("KOSPI")
        # assert kospi_result is not None
        try:
            error_result = self.ebest.get_code_list("kospi")
        except:
            error_result = None
        assert error_result is None

        # print(f"result : ALL {len(all_result)} KOSPI {len(kospi_result)} KOSDAQ {len(kosdaq_result)}")
        print(f"result : ALL {len(all_result)}  KOSDAQ {len(kosdaq_result)}")

    def _test_historical_closing_price(self):
        closing = self.ebest.get_historical_closing_price('005930', startdate='20100101', enddate='20220107')
        df_closing = pd.DataFrame(closing)
        type(df_closing)
        df_closing['close'] = pd.to_numeric(df_closing['close'], errors='coerce')
        df_closing['date'] = pd.to_datetime(df_closing['date'], errors='coerce')

        # MA
        ma_range = [5, 25, 120, 250]
        # ma_color = ['red', 'yellow', 'pink', 'black']
        for i in range(len(ma_range)):
            df_closing[f"ma{ma_range[i]}"] = df_closing['close'].rolling(window=ma_range[i]).mean()

        print(df_closing.head())
        ### plot test
        ax = plt.gca()
        df_closing.plot(kind='line', x='date', y='close', ax=ax)

        for i in range(len(ma_range)):
            df_closing.plot(kind='line', x='date', y=f'ma{ma_range[i]}', ax=ax)

        plt.show()

    def _test_get_account_info(self):
        print(inspect.stack()[0][3])  # test명
        lst_acno = self.ebest.get_account()
        print(lst_acno)

    def _test_get_account(self):
        acc_info = self.ebest.get_account_info()
        assert acc_info is not None
        print(acc_info)

    def _test_get_account_stock_info(self):
        stock_info = self.ebest.get_account_stock_info()
        assert stock_info is not None
        print(stock_info)

    def _test_get_stock_price_by_code(self):
        close = self.ebest.get_stock_price_by_code('000020', 1, 1)
        assert close is not None
        print(close)

    def _test_get_0424(self):
        result = self.ebest.get_0424()
        print(result)



    def _test_buy_stock_by_best_offer(self):
        best_offer = self.ebest.get_current_price_by_code('005930')
        offer_price = best_offer[0]['bidho1']
        print(offer_price)
        result = self.ebest.order_stock('005930', 1, float(offer_price), "2", "00")
        assert result is not None
        print(result)



    def _test_order_cancel_stock(self):
        # 주문먼저하고..
        res = self.ebest.order_stock("005930", 6, 71100, "2", "00")
        time.sleep(1)
        ordno = res[0]["OrdNo"]
        print(ordno)

        #serial cancel
        for i in range(6):
            cancel_res = self.ebest.order_cancel(ordno, "005930", 1)
            # time.sleep(0.1)

    def _test_get_current_price_by_code(self):
        result=self.ebest.get_current_price_by_code('005930')
        print(result)



    def _test_order_cancel_stock(self):
        # 주문먼저하고..
        res = ebest.order_stock("005930", 6, 71100, "2", "00")
        print("원주문", res)
        ordno = res[0]["OrdNo"]

        #1주 취소
        cancel_res = ebest.order_cancel(ordno, "005930", 1)
        if cancel_res is not None:
            cancel_res2 = ebest.order_cancel(ordno, "005930", 1)
            if cancel_res2 is not None:
                cancel_res3 = ebest.order_cancel(ordno, "005930", 1)
                if cancel_res3 is not None:
                    cancel_res4 = ebest.order_cancel(ordno, "005930", 1)
                    if cancel_res4 is not None:
                        cancel_res5 = ebest.order_cancel(ordno, "005930", 1)
                        if cancel_res5 is not None:
                            cancel_res6 = ebest.order_cancel(ordno, "005930", 1)

    def _test_trading_scenario(self):
        #주문내역 DB삭제하기
        ordered_list=list(mongo.find_items({},DB_NAME,'order'))
        if ordered_list is not None:
            mongo.delete_items({},DB_NAME, 'order')

        ordered_list = list(mongo.find_items({}, DB_NAME, 'order'))
        assert len(ordered_list)==0


        code_list=['005930']
        for code in code_list:
            time.sleep(1)
            result = self.ebest.get_current_price_by_code(code)
            current_price = result[0]['price']
            print(f"current price of {result[0]['hname']} is ", current_price)
            """check buy order"""
            buy_order_cnt = check_buy_order(code)
            check_buy_completed_order(code)

            if buy_order_cnt == 0:
                """보유 종목 없을시 무조건(as a strategy) 신규매수 """
                order = self.ebest.order_stock(code, "2", current_price, "2", "00")
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

            # check_sell_order(code)

    def test_order_check(self):
        # 주문먼저하고
        # ord=self.ebest.order_stock('005930', 7, 71500, "2", "00")
        # time.sleep(1)
        # if ord:
        #     res=self.ebest.order_check()
        #     print(res)

        check_not_traded_order=self.ebest.order_check()
        print(check_not_traded_order)

    def tearDown(self):
        self.ebest.logout()



def check_buy_completed_order(code):
    """매수 체결 여부 체크"""
    buy_completed_order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_completed"}]},
                                                     DB_NAME, "order"))

def check_buy_order(code):
    """매수 주문 완료 여부 체크"""
    order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_ordered"}]},
                                       DB_NAME, "order"))
    for order in order_list:
        time.sleep(1)
        code = order['code']  # order['shcode']?
        order_no = order['buy_order_doc']['OrdNo']
        order_cnt = order['buy_order_doc']['SpotOrdQty']
        check_result = ebest_demo.order_check(order_no) #체결/미체결여부 확인
        print("'check buy order result", check_result)
        result_cnt = check_result['traded_amt']
        if order_cnt == result_cnt:
            mongo.update_item({"order_no": order_no},
                              {"$set": {"buy_completed": check_result, "status": "buy_completed"}},
                              DB_NAME, "order")

            print("buy_completed", check_result)

    return len(order_list)

if __name__ == "__main__":
    unittest.main()
