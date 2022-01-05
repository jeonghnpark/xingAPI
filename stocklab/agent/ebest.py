import configparser
import time
from datetime import datetime
import pythoncom
import win32com.client

import os

import csv


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
        print("OnReceiveData", code)
        XAQuery.tr_run_state = 1

    def OnReceiveMessage(self, error, code, message):
        print("OnReceiveMessage", error, code, message, XAQuery.tr_run_state)


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
    LIMIT_SECONDS = 600  # 10분

    def __init__(self, mode=None):
        """
        config.ini를 로드함
        query_cnt 10분당 200개의 쿼리 처리
        xa_session_client 는 XASession객체
        :param mode: str -모의서버는 DEMO, 실서버는 PROD로 구별
        """
        if mode not in ["PROD", "DEMO"]:
            raise Exception("Need run_mode(PROD or DEMO)")

        run_mode = "EBEST_" + mode
        config = configparser.ConfigParser()
        config.read('D:\\dev\python\\xingAPI\\stocklab\\agent\\conf\\config.ini')

        self.user = config[run_mode]['user']
        self.passwd = config[run_mode]['password']
        self.cert_passwd = config[run_mode]['cert_passwd']
        self.host = config[run_mode]['host']
        self.port = config[run_mode]['port']
        self.account = config[run_mode]['account']

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
                print("waiting..^^", self.xa_session_client.GetLastError())
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

    def get_current_call_price_by_code(self, code=None):
        """ TR: t1101 주식현재가 호가 조회
        :param code:str 종목코드 
        :return: 
        """
        tr_code = 't1101'
        in_params = {"shcode": code}
        out_params = {"hname", "price", "sign", "change", "diff", "volume",
                      "jnilclose", "offerho1", "bidho1", "offerrem1", "bidrem1",
                      "offerho2", "bidho2", "offerrem2", "bidrem2"}

        result = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + 'OutBlock', *out_params, **in_params)

        for item in result:
            item["code"] = code

        return result

    def get_code_list(self, market=None):
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
        accnum = self.xa_session_client.GetAccountListCount()
        accountList = []
        for i in range(accnum):
            accountList = self.xa_session_client.GetAccountList(i)
            print(accountList)
        return accountList

    def get_historical_closing_price(self, code=None, frequency=2, startdate='20210101', enddate='20211231',
                                     comp_yn="N"):
        tr_code = 't8413'
        in_params = {'shcode': code, 'gubun': frequency, 'sdate': startdate, 'edate': enddate, 'comp_yn': comp_yn}
        out_params = {'date', 'close', 'jdiff_vol'}
        closing_price = self._execute_query(tr_code, tr_code + 'InBlock', tr_code + "OutBlock1", *out_params,
                                            **in_params)
        return closing_price


if __name__ == "__main__":
    session = EBest("DEMO")
    # print(session.user)
    session.login()

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

    all_result = session.get_code_list("ALL")
    assert all_result is not None
    print(f"all result {len(all_result)}")

    kosdaq_result = session.get_code_list("KOSDAQ")
    assert kosdaq_result is not None
    print(f"kosdaq result {len(kosdaq_result)}")

    kosdaq_result = session.get_code_list("KOSPI")
    assert kosdaq_result is not None
    print(f"kosdaq result {len(kosdaq_result)}")

    # kospi_result = session.get_code_list("KOSPI")
    # assert kospi_result is not None
    # session.logout()
