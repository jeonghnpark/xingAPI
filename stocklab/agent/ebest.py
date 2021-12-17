import configparser


class XASession:
    login_state=0


    def OnLogin(self, code, msg):
        if code=="0000":
            print(code, msg)
            XASession.login_state=1
        else:
            print(code, msg)


    def OnDisconnect(self):
        print("Session disconnected")
        XASession.login_state=0


class XAQuery:
    RES_PATH="C:\\eBest\\xingAPI\\Res\\"
    tr_run


class EBEst:

    def __init__(self, mode=None):
        """
        config.ini를 로드함
        query_cnt 10분당 200개의 쿼리 처리
        xa_session_client 는 XASession객체
        :param mode: str -모의서버는 DEMO, 실서버는 PROD로 구별
        """
        if mode not in ["PROD", "DEMO"]:
            raise Exception("Need run_mode(PROD or DEMO)")

        run_mode="EBEST_"+mode
        config=configparser.ConfigParser()
        config.read('conf/config.ini')
        self.user=config[run_mode]['user']



session=EBEst("DEMO")
print(session.user)




