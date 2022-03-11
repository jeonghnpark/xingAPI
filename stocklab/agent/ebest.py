import configparser
import time
from datetime import datetime
import pythoncom
import win32com.client

import os

import csv

from stocklab.db_handler.mongodb_handler import MongoDBHandler

import pandas as pd

class XASession:
    login_state = 0

    def OnLogin(self, code, msg):
        if code == "0000":
            print(code, msg)
            XASession.login_state = 1
        else:
            print(code, msg)

    def OnDisconnect(self):
        print("Session disconnected")
        XASession.login_state = 0


class XAQuery:
    RES_PATH = "C:\\eBest\\xingAPI\\Res\\"
    tr_run_state = 0

    def OnReceiveData(self, code):
        print("MyOnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("MyOnReceiveMessage", "error-> ", error, "code ->", code, message, "XAQuery.tr_run_state->",
              XAQuery.tr_run_state)


class XAReal:
    RES_PATH = "C:\\eBest\\xingAPI\\Res\\"

    def register_code(self, code):
        print("register code", code)
        self.LoadFromResFile(XAReal.RES_PATH + "K3_.res")
        self.SetFieldData("InBlock", "shcode", code)
        self.AdviseRealData()

    def OnReceiveRealData(self, tr_code):
        print("tr_code", tr_code)
        result = []
        for field in ["chetime", "sign", "change", "price", "opentime", "open",
                      "hightime", "high", "lowtime"]:
            value = self.GetFieldData("OutBlock", field)
            item[field] = value
            result.append(item)
        print(result)


class EBest:
    QUERY_LIMIT_10MIN = 200  # 10분당 최대 200개 쿼리, 초과하는 경우 연결 끊김, 초당 3건??
    LIMIT_SECONDS = 600  # 10분=600초

    def __init__(self, mode=None):
        """
        config.ini를 로드함
        query_cnt 10분당 200개의 쿼리 처리
        xa_session_client 는 XASession객체
        :param mode: str -모의서버는 DEMO, 실서버는 PROD로 구별
        """
        if mode not in ["PROD", "DEMO", "ACE"]:
            raise Exception("Need run_mode(PROD or DEMO or ACE)")

        run_mode = "EBEST_" + mode
        config = configparser.ConfigParser()
        config.read('D:\\dev\python\\xingAPI\\stocklab\\agent\\conf\\config.ini')

        self.user = config[run_mode]['user']
        self.passwd = config[run_mode]['password']
        self.cert_passwd = config[run_mode]['cert_passwd']
        self.host = config[run_mode]['host']
        self.port = config[run_mode]['port']
        self.account = config[run_mode]['account']
        self.account_deriva = config[run_mode]['account_deriva']

        # COM객체를 만든다. 인자1: COM 이름, 인자2:이벤트 콜백시 호출될 클래스
        # 콜백시 호출될 클래스에는 Login()과 Disconnect() 메서드가 정의되어있으면
        # 해당 이벤트가 실행된다.
        # 특이하게 두번째 인자는 클래스이 인스턴스가 아니라 클래스명이 들어감
        # DispatchWithEvents로  COM 객체를 만들면 콜백함수들도 다중 상속되어
        # 객체가 만들어지므로 콜백 클래스의 기능을 쓸수 있다고 한다.. 뭔말인지

        self.xa_session_client = win32com.client.DispatchWithEvents("XA_Session.XASession", XASession)

        self.query_cnt = []

    def login(self):
        self.xa_session_client.ConnectServer(self.host, self.port)
        self.xa_session_client.Login(self.user, self.passwd, self.cert_passwd, 0, 0)
        while XASession.login_state == 0:
            pythoncom.PumpWaitingMessages()

    def logout(self):
        XASession.login_state = 0
        self.xa_session_client.DisconnectServer()

    def _execute_query(self, res, in_block_name, out_block_name, *out_fields, **set_fields):
        print("current query cnt:", len(self.query_cnt))
        print(res, in_block_name, out_block_name)
        while len(self.query_cnt) >= EBest.QUERY_LIMIT_10MIN:
            time.sleep(1)
            print("waiting for execute query.. current query cnt:", len(self.query_cnt))
            print(f"남은 시간: {int(EBest.LIMIT_SECONDS) - (datetime.today() - self.query_cnt[0]).total_seconds()}초")
            self.query_cnt = list(
                filter(lambda x: (datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt))
            # 오래된 쿼리를 삭제하나?? -> OK. 쿼리는 한번에 하나씩 실행됨. 밀려서 실행하지 않음. 응답을 받을때까지 쿼리를 종료하지 않음
        xa_query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQuery)
        xa_query.LoadFromResFile(XAQuery.RES_PATH + res + ".res")

        # in_block_name 세팅
        for key, value in set_fields.items():
            xa_query.SetFieldData(in_block_name, key, 0, value)  # 3번째 인수는 단일 데이터-> 0

        errorCode = xa_query.Request(0)

        # 요청후 대기 응답을 받을때까지 쿼리를 종료하지 않음
        waiting_cnt = 0
        while xa_query.tr_run_state == 0:
            waiting_cnt += 1
            if waiting_cnt % 1000000 == 0:
                print("개별 쿼리의 응답이 늦어지고 있어요..^^", self.xa_session_client.GetLastError())
            pythoncom.PumpWaitingMessages()

        # result block
        result = []
        count = xa_query.GetBlockCount(out_block_name)  # OCCUR인 경우가 >1 이라고 함

        for i in range(count):
            item = {}
            for field in out_fields:
                value = xa_query.GetFieldData(out_block_name, field, i)
                item[field] = value
            result.append(item)

        XAQuery.tr_run_state = 0  # static variable why?
        self.query_cnt.append(datetime.today())

        # from  English field to Korean field
        # for item in result:
        #     for field in list(item.keys()):
        #         if getattr(Field, res, None):
        #             res_field = getattr(Field, res, None)

        return result

    def get_stock_price_by_code(self, code=None, dwmcode=1, cnt="1"):
        """TR1505 기간별주가
        code: str (6)
        dwmcode: long, 1:일, 2: 주, 3: 월
        """

        tr_code = 't1305'
        in_params = {'shcode': code, 'dwmcode': '1', 'date': "", 'idx': "", 'cnt': cnt}
        out_params = {"date", 'shcode', 'close'}
        result = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + 'OutBlock1', *out_params, **in_params)

        for item in result:
            item['code'] = code

        return result

    def get_tick_size(self, price):
        if price < 1000:
            return 1
        elif price >= 1000 and price < 5000:
            return 5
        elif price >= 5000 and price < 10000:
            return 10
        elif price >= 10000 and price < 50000:
            return 50
        elif price >= 50000 and price < 100000:
            return 100
        elif price >= 100000 and price < 500000:
            return 500
        elif price > 500000:
            return 1000


    def get_code_list(self, market=None):
        """market='KOSPI', 'KOSDAQ', 'ALL' """
        tr_code = 't8436'
        if market not in ['KOSPI', 'KOSDAQ', 'ALL']:
            raise Exception("need market param('ALL','KOSPI','KOSDAQ')")
        market_code = {"ALL": "0", "KOSPI": "1", "KOSDAQ": "2"}
        in_params = {'gubun': market_code[market]}
        out_params = {'hanme', 'shcode', 'expcode', 'etfgubun', 'memedan', 'gubun', 'spac_gubun'}
        result = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + "OutBlock", *out_params, **in_params)
        return result

    def get_all_stock_info(self, market=None):

        tr_code = 't8430'
        marketcode = 1
        if market == "KOSPI":
            marketcode = 1
        elif market == "KOSDAQ":
            markecode = 2
        elif market == "ALL":
            marketcode = 0

        in_params = {'gubun': marketcode}
        out_params = {"hname", "jnilclose", "shcode"}
        stocks = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + 'OutBlock', *out_params, **in_params)

        file = open('stock_info.csv', 'w')
        writer = csv.writer(file)
        writer.writerow(['종목명', "종목코드", "전일가"])
        for stock in stocks:
            writer.writerow([stock['hname'], str(stock['shcode']), stock['jnilclose']])

        return stocks

    def get_account(self):
        """:return accountList:List"""
        accnum = self.xa_session_client.GetAccountListCount()
        accountList = []
        for i in range(accnum):
            accountList = self.xa_session_client.GetAccountList(i)
            # print(accountList)
        return accountList

    def get_account_stock_info(self):
        """현물계좌잔고내역
        TR:CSPAQ12300
        :param
        res: str
        in_block_name: str
        out_block_name: str

        in_params: dictionary
            RecCnt: long 레코드개수
            AcntNo: str
            Pwd: str
            BalCreTp: str (잔고생성구분 0:전체, 1:현물, 9:선물대용),
            D2balBaseQryTp:str D2잔고기준조회, 0:전부조회, 1:D2잔고 0 이상만
            in_block_name: str
            out_blcok_name: str

        out_params: list
            IsuNo 종목번호
            IsuNm 종목명
            BalQty 잔고수량
            SellPrc 매도가
            BuyPrc 매수가
            NowPrc 현재가
            AvrUprc 평균단가
            BalEvalAmt 잔고평가금액
            PrdayCprc 전일종가
        """

        tr = "CSPAQ12300"
        in_params = {"RecCnt": 1, "AcntNo": self.account, "Pwd": self.passwd,
                     "BalCreTp": "0", "D2balBaseQryTp": "0"}
        out_params = ["IsuNo", "IsuNm", "BalQty", "SellPrc", "BuyPrc",
                      "AvrUprc", "BalEvalAmt", "PrdayCprc"]

        result = self._execute_query(tr, tr + "InBlock1", tr + "OutBlock3", *out_params, **in_params)

        return result

    def get_account_info(self):
        """TR:CSPAQ12200 현물계좌  예수금/주문가능금액/총평가
        :param
        in_params = {"RecCnt": 1, "AcntNo": self.user, "Pwd": self.passwd}
                      레코드개수?, 계좌번호, 비밀번호
        :return result:list
        ["MnyOrdAbleAmt", "BalEvalAmt", "DpsastTotamt", "InvstOrgAmt", "InvstPlAmt"]
        [현금주문가능금액, 잔고평가금액, 예탁자산총액, 투자원금, 투자손익금액]
        """
        tr = "CSPAQ12200"
        in_params = {"RecCnt": 1, "AcntNo": self.account, "Pwd": self.passwd}
        out_params = ["MnyOrdAbleAmt", "BalEvalAmt", "DpsastTotamt", "InvstOrgAmt", "InvstPlAmt"]

        result = self._execute_query(tr, tr + "InBlock1", tr + "OutBlock2", *out_params, **in_params)

        return result

    def get_historical_closing_price(self, code=None, frequency=2, startdate='20210101', enddate='20211231',
                                     comp_yn="N"):
        tr_code = 't8413'
        in_params = {'shcode': code, 'gubun': frequency, 'sdate': startdate, 'edate': enddate, 'comp_yn': comp_yn}
        out_params = {'date', 'close', 'jdiff_vol'}
        closing_price = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + "OutBlock1", *out_params,
                                            **in_params)
        return closing_price

    def chart_min(self, code=None, ncnt=None, qrycnt=None, edate=None, cts_date='', cts_time=' '):
        time.sleep(0.5)
        tr_code = 't8412'

        MYNAME = tr_code
        INBLOCK = f"{MYNAME}InBlock"
        INBLOCK1 = f"{MYNAME}InBlock1"
        OUTBLOCK = f"{MYNAME}OutBlock"
        OUTBLOCK1 = f"{MYNAME}OutBlock1"
        OUTBLOCK2 = f"{MYNAME}OutBlock2"

    def get_0424(self):
        """주식 잔고조회"""
        tr_code = 't0424'
        in_params = {'accno': self.account, 'passwd': self.passwd,
                     'prcgb': 1, 'chegb': 0, 'charge': 1}
        out_params = {'tappamt'}
        result = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + "OutBlock", *out_params,
                                     **in_params)
        return result

    def order_cancel(self, order_no, code, qty):
        """TR-> CSPAT00800
        """
        tr = "CSPAT00800"
        in_params = {"OrgOrdNo": order_no, "AcntNo": self.account, "InptPwd": self.passwd,
                     "IsuNo": code, "OrdQty": qty}
        # 블록: InBlcok1
        out_params = ["OrdNo", "PrntOrdNo", "OrdTime", "OrdPtnCode", "IsuNm"]
        # 블록: OutBlcok2
        # PrntOrdNo(long):모주문번호, OrdPtnCode(str) : 주문유형코드, IsuNm(str):종목명

        result = self._execute_query(tr, tr + "InBlock1", tr + "OutBlock2", *out_params, **in_params)
        return result

    def order_stock(self, code, qty, price, bns_type, order_type):
        """TR -> CSPAT00600, 현물 정상 주문
            입력블록명: InBlock1
            출력블록명: OutBlock2

            :param
            code: str
            qty: long
            price : double
            bns_type: str 매매구분 "1"-매도, "2"-매수
            order_type: str 호가유형코드 "00"@ 지정가, "03"@시장가, "06"@최유리지정가, "07"@최우선지정가

            :return
            result: list of dict -> result[0]으로 받아야함.
                OrdNo: long
                OrdTime: str
                OrdMktCode: str , 주문시장코드
                OrdPtnCode: str, 주문유형코드
                ShtnIsuNo: str, 단축종목코드
                MgempNo: str,  관리사원번호 -> 삭제
                OrdAmt: long, 주문금액
                SpotOrdQty: long, 실주문수량
                IsuNm: str, 종목명
        """
        tr = "CSPAT00600"
        in_params = {"AcntNo": self.account, "InptPwd": self.passwd, "IsuNo": code, "OrdQty": qty,
                     "OrdPrc": price, "BnsTpCode": bns_type, "OrdprcPtnCode": order_type, "MgntrnCode": "000",
                     "LoanDt": "", "OrdCndiTpCode": "0"}
        out_params = ["OrdNo", "OrdTime", "OrdMktCode", "OrdPtnCode", "ShtnIsuNo", "OrdAmt", "SpotOrdQty", "IsuNm"]
        # 블록 OutBlock2
        #

        result = self._execute_query(tr, tr + "InBlock1", tr + "OutBlock2", *out_params, **in_params)
        return result

    def get_current_price_by_code(self,code):
        """TR:t1101
        현재 호가조회
        return: list
        리턴값이 list이므로 result[0]으로 받아야함 why?
        """
        tr='t1101'
        in_params={"shcode":code}
        out_params={"hname", "price", "offerho1", "bidho1", "offerho2", 'bidho2', 'offerrem1', 'offerrem2',
                    "bidrem1", 'bidrem2'}
        result=self._execute_query(tr, tr+"InBlock", tr+"OutBlock",*out_params, **in_params)

        for item in result:
            item["code"]=code

        return result

    # def get_current_call_price_by_code(self, code=None):
    #     """ TR: t1101 주식현재가 호가 조회
    #     :param code:str 종목코드
    #     :return:
    #     """
    #     tr_code = 't1101'
    #     in_params = {"shcode": code}
    #     out_params = {"hname", "price", "sign", "change", "diff", "volume",
    #                   "jnilclose", "offerho1", "bidho1", "offerrem1", "bidrem1",
    #                   "offerho2", "bidho2", "offerrem2", "bidrem2"}
    #
    #     result = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + 'OutBlock', *out_params, **in_params)
    #
    #     for item in result:
    #         item["code"] = code
    #
    #     return result


    def order_check(self, order_no=None, traded_or_not="0"):
        """TR:t0425
        체결미체결 여부 확인, 초당 1건
        traded_or_not : "0"->전체, "1"->체결, "2"->미체결
        입력블록 t0425InBlock
        출력블록 t0425OutBlock1
        ordno, expcode, price(주문가격), cheprice(체결가격), cheqty(체결수량), ordrem(미체결잔량)
        """
        tr="t0425"
        in_params={"accno":self.account, "passwd": self.passwd, "expcode":"", "chegb": traded_or_not,
                   "medosu": "0", "sortgb":"1", "cts_ordno": ""}
        out_params=["ordno", "expcode", "medosu", "qty", "price", "cheqty", "cheprice",
                    "ordrem", "cfmqty", "status", "orgordno", "ordgb", "ordermtd", "sysprocseq",
                    "hodagb", "price1", "orggb", "singb", "loandt"]

        result_list=self._execute_query(tr,tr+"InBlock", tr+"OutBlock1", *out_params, **in_params)
        result={}
        if order_no is not None:
            for item in result_list:
                if item['ordno']==order_no:
                    result=item

            return result  # 주문번호를 입력하지 않으면 list 전체를, 주문번호 입력시는 주문번호만 리턴
        else:
            return result_list


    def order_check2(self,order_no=None,traded_or_not="0"):
        """TR: CSPAQ13700"""
        tr="CSPAQ13700"
        in_params={"RecCnt":"1","AcntNo":self.account, "InptPwd":self.passwd,
                   }
    def get_tick_size(self,price):
        if price<1000:
            return 1
        elif price>=1000 and price<5000:
            return 5
        elif price >= 5000 and price < 10000:
            return 10
        elif price >= 10000 and price < 50000:
            return 50
        elif price >= 50000 and price < 100000:
            return 100
        elif price >= 100000 and price < 500000:
            return 500
        elif price >= 500000:
            return 1000


    def get_price_n_min_by_code(self,date, code, tick=None):
        """TR=tr8412
        주식 분차트(N분)
        :params: tick:long n-> n분, 0-> 30초
        :return:result: tick=None인 경우 dict, tick=None인 경우 list of dict
        """
        tr="t8412"
        """in_params
        :params: "ncnt":"0"->0.5분, "1" -> 1분, 2->2분
        """
        in_params={"shcode":code, "ncnt": "1", "qrycnt":"500", "nday":"1", "sdate": date,
                   "stime": "090000", "edate":date, "etime": "153000",
                   "cts_date":"00000000", "cts_time":"0000000000", "comp_yn":"N"}

        out_params=["date", "time", "open", "high", "low","close", "jdiff_vol", "value"]
        
        result_list=self._execute_query(tr, tr+'InBlock', tr+'OutBlock1', *out_params, **in_params)

        result=[]
        for idx, item in enumerate(result_list):
            # result[idx]=item
            result.append(item)

        if tick is not None:
            return result[tick]

        return result

if __name__ == "__main__":
    pass
    # ebest = EBest("DEMO")
    # ebest.login()
    # res = ebest.order_stock("005930", 6, 80000, "2", "00")
    # print(res)
    # ebest.logout()

    # ebest = EBest("DEMO")
    # ebest.login()
    # res = ebest.order_stock("005930", 6, 71600, "2", "00")
    # print("원주문", res)
    # ordno = res[0]["OrdNo"]
    # 
    # # time.sleep(1)
    # cancel_res = ebest.order_cancel(ordno, "005930", 1)
    # # if cancel_res is not None:
    # #     print("첫 취소주문", cancel_res)
    # 
    # # time.sleep(1)
    # if cancel_res is not None:
    #     cancel_res2 = ebest.order_cancel(ordno, "005930", 1)
    #     if cancel_res2 is not None:
    #         cancel_res3 = ebest.order_cancel(ordno, "005930", 1)
    #         if cancel_res3 is not None:
    #             cancel_res4 = ebest.order_cancel(ordno, "005930", 1)
    #             if cancel_res4 is not None:
    #                 cancel_res5 = ebest.order_cancel(ordno, "005930", 1)
    #                 if cancel_res5 is not None:
    #                     cancel_res6 = ebest.order_cancel(ordno, "005930", 1)

    # cancel_res2 = ebest.order_cancel(ordno, "005930", 1)
    # cancel_res2 = ebest.order_cancel(ordno, "005930", 1)
    # if cancel_res2 is not None:
    #     print("첫 취소주문", cancel_res2)

    # time.sleep(1)
    # cancel_res2 = ebest.order_cancel(ordno, "005930", 2)
    # if cancel_res2 is not None:
    #     print(cancel_res2)

    # close = session.get_stock_price_by_code('005930', 1, 6)
    # df_close = pd.DataFrame(close)
    # print(df_close)

    # balance = session.get_0424()
    # print(balance)
    # result = session.get_current_call_price_by_code("005930")
    # print(f"price={result[0]['price']}")
    # accList = session.get_account()
    # print(accList)
    #
    # kospi_all_stock = session.get_all_stock_info("KOSPI")
    # print(kospi_all_stock)
    # print(kospi_all_stock)
    # closing_prices = session.get_historical_closing_price('005930')

    # print('date      closing price    volume')
    # for d in closing_prices:
    #     print(f"{d['date']}  {d['close']}  {d['jdiff_vol']}")
    # code_list = session.get_code_list("KOSPI")
    # print(code_list)

    # all_result = session.get_code_list("ALL")
    # assert all_result is not None
    # print(f"all result {len(all_result)}")
    # 
    # kosdaq_result = session.get_code_list("KOSDAQ")
    # assert kosdaq_result is not None
    # print(f"kosdaq result {len(kosdaq_result)}")
    # 
    # kosdaq_result = session.get_code_list("KOSPI")
    # assert kosdaq_result is not None
    # print(f"kosdaq result {len(kosdaq_result)}")

    # kospi_result = session.get_code_list("KOSPI")
    # assert kospi_result is not None
    # session.logout()
