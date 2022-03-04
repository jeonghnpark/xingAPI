import unittest
from stocklab.agent.ebest import EBest

import inspect
import time
import pandas as pd
import matplotlib.pyplot as plt

from stocklab.db_handler.mongodb_handler import MongoDBHandler
mongo=MongoDBHandler()
DB_NAME="stocklab_ace"
ebest_ace=EBest("ACE")


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

        """ 주문내역 DB삭제"""
        # ordered_list=list(mongo.find_items({},DB_NAME,'order'))
        # if ordered_list is not None:
        #     mongo.delete_items({},DB_NAME, 'order')
        # #삭제확인
        # ordered_list = list(mongo.find_items({}, DB_NAME, 'order'))
        # assert len(ordered_list)==0


        code_list=['005930']
        for code in code_list:
            time.sleep(1)
            result = self.ebest.get_current_price_by_code(code)
            current_price = result[0]['price']
            print(f"current price of {result[0]['hname']} is ", current_price)

            # buy_order_cnt = check_buy_order(code) #체결여부 확인후 체결되었다면 상태변경

            """ DB에서 매수가 들어간 목록에 대해서
            ebest에 쿼리하여 체결여부를 확인한후 체결되었다면
            DB의 상태를 변경함"""
            order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_ordered"}]},
                                               DB_NAME, "order"))
            for order in order_list:  #
                time.sleep(1)
                code = order['code']  # order['shcode']?
                order_no = order['buy_order_doc']['OrdNo']
                order_cnt = order['buy_order_doc']['SpotOrdQty']  # 실주문수량
                check_result = self.ebest.order_check(order_no)  # 쿼리하여 체결/미체결여부 확인

                print("'check buy order result", check_result)
                result_cnt = check_result['cheqty']  # 체결수량
                if order_cnt == result_cnt:
                    mongo.update_item({"buy_order_doc.OrdNo": order_no},
                                      {"$set": {"buy_completed_doc": check_result, "status": "buy_completed"}},
                                      DB_NAME, "order")

                    print("buy_completed", check_result)

            #check_buy_completed_order(code) # 매수완료되었다면 매도 주문
            """매수 완료된 주문에 대해서 10틱위로 매도 주문 넣기"""
            buy_completed_order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_completed"}]},
                                                             DB_NAME, "order"))
            """매도 주문"""
            for buy_completed_order in buy_completed_order_list:
                buy_price = buy_completed_order['buy_completed_doc']['price']  # 체결가격
                buy_order_no = buy_completed_order['buy_completed_doc']['ordno']
                tick_size = self.ebest.get_tick_size(int(buy_price))
                print('tick size', tick_size)
                sell_price = int(buy_price) + tick_size * 10
                sell_order = self.ebest.order_stock(code, "2", str(sell_price), "1", "00")
                print("order_stock", sell_order)
                mongo.update_item({"buy_completed_doc.ordno": buy_order_no},
                                  {"$set": {"sell_order_doc": sell_order[0], "status": "sell_ordered"}},
                                  DB_NAME, "order")  # TODO : sell_order[0] why?

            '''보유 종목 없을시 무조건(as a strategy) 신규매수'''
            buy_order_cnt=len(order_list)

            if buy_order_cnt == 0:
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
        """주문먼저하고"""
        current=self.ebest.get_current_price_by_code('005930')
        time.sleep(1)
        print(current[0]['price'])
        ord=self.ebest.order_stock('005930', 3, current[0]['price'], "2", "00")
        time.sleep(1)
        # if ord:
        #     res=self.ebest.order_check()
        #     print(res)

        check_not_traded_order=self.ebest.order_check(ord[0]['OrdNo'])
        for order in check_not_traded_order:
            print(check_not_traded_order)

    def tearDown(self):
        self.ebest.logout()


# def check_buy_completed_order(code):
#     """매수 완료된 주문은 매도 주문
#     """
#     buy_completed_order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_completed"}]},
#                                                      DB_NAME, "order"))
#
#     # 매도 주문
#     for buy_completed_order in buy_completed_order_list:
#         buy_price = buy_completed_order['buy_completed_doc']['price']  # 체결가격
#         buy_order_no = buy_completed_order['buy_completed_doc']['ordno']
#         tick_size = ebest_ace.get_tick_size(int(buy_price))
#         print('tick size', tick_size)
#         sell_price = int(buy_price) + tick_size * 10
#         sell_order = ebest_ace.order_stock(code, "2", str(sell_price), "1", "00")
#         print("order_stock", sell_order)
#         mongo.update_item({"buy_completed_doc.ordno": buy_order_no},
#                           {"$set": {"sell_order_doc": sell_order[0], "status": "sell_ordered"}},
#                           DB_NAME, "order")  # TODO : sell_order[0] why?
#
#
# def check_buy_order(code):
#     """ DB에서 매수가 들어간 목록에 대해서
#     ebest에 쿼리하여 체결여부를 확인한후 체결되었다면
#     DB의 상태를 변경함"""
#     order_list = list(mongo.find_items({"$and": [{"code": code}, {"status": "buy_ordered"}]},
#                                        DB_NAME, "order"))
#     for order in order_list:  #
#         time.sleep(1)
#         code = order['code']  # order['shcode']?
#         order_no = order['buy_order_doc']['OrdNo']
#         order_cnt = order['buy_order_doc']['SpotOrdQty']  # 실주문수량
#         check_result = ebest_ace.order_check(order_no)  # 쿼리하여 체결/미체결여부 확인
#
#         print("'check buy order result", check_result)
#         result_cnt = check_result['cheqty']  # 체결수량
#         if order_cnt == result_cnt:
#             mongo.update_item({"buy_order_doc.OrdNo": order_no},
#                               {"$set": {"buy_completed_doc": check_result, "status": "buy_completed"}},
#                               DB_NAME, "order")
#
#             print("buy_completed", check_result)
#
#     return len(order_list)

if __name__ == "__main__":
    unittest.main()
