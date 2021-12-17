import configparser

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
    QUERY_LIMIT_10MIN = 200
    LIMIT_SECONDS = 600

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

        self.xa_session_client = win32com.client.DispatchWithEvents("XA_Session.XASession", XASession)

        self.query_cnt = []

    def login(self):
        pass


session = EBEst("DEMO")
print(session.user)
