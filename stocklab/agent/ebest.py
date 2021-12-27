import configparser
import time
from datetime import datetime
import pythoncom
import win32com.client


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


class EBEst:
    QUERY_LIMIT_10MIN = 200  # 10분당 최대 200개 쿼리, 초과하는 경우 연결 끊김
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
        config.read('conf/config.ini')
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
        while len(self.query_cnt) >= EBEst.QUERY_LIMIT_10MIN:
            time.sleep(1)
            print("waiting for execute query.. current query cnt:", len(self.query_cnt))
            self.query_cnt = list(
                filter(lambda x: (datetime.today() - x).total_seconds() < EBest.LIMIT_SECONDS, self.query_cnt))
            # 오래된 쿼리를 삭제하나?? 
        xa_query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQuery)
        xa_query.LoadFromResFile(XAQuery.RES_PATH + res + ".res")

        # in_block_name 세팅
        for key, value in set_fields.items():
            xa_query.SetFieldData(in_block_name, key, 0, value)

        errorCode = xa_query.Request(0)

        # 요청후 대기
        waiting_cnt = 0
        while xa_query.tr_run_state == 0:
            waiting_cnt += 1
            if waiting_cnt % 1000000 == 0:
                print("waiting..", self.xa_session_client.GetLastError())
            pythoncom.PumpWaitingMessages()

        # result block
        result = []
        count = xa_query.GetBlockCount(out_block_name)

        for i in range(count):
            item = {}
            for field in out_fields:
                value = xa_query.GetFieldData(out_block_name, field, i)
                item[field] = value
            result.append(item)

        XAQuery.tr_run_state = 0  # static variable why?
        self.query_cnt.append(datetime.today())

        # from  English field to Korean field
        for item in result:
            for field in list(item.keys()):
                if getattr(Field, res, None):
                    res_field = getattr(Field, res, None)
                    

session = EBEst("DEMO")
print(session.user)
