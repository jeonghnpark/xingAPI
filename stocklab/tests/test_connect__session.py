import win32com.client
import pythoncom

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


client = win32com.client.Dispatch("XA_Session.XASession", XASession)
client.ConnectServer("demo.ebestsec.co.kr", 20001)
client.Login('tunan', 'hn141437','',0,0)

while XASession.login_state==0:
    pythoncom.PumpWaitingMessages()

# self.xa_session_client.Login(self.user, self.passwd, self.cert_passwd, 0, 0)

# print(client)
# # client.DisconnectServer()
#
# import time
# from datetime import datetime
#
# # , timedelta
#
# # from datetime.timedelta import total_seconds
#
# # print(datetime.today())
#
# # print((datetime.today() - 3).total_second())
#
# dt1 = datetime(2016, 1, 2, 14)
# dt2 = datetime(2016, 1, 2, 15)
# dt3 = datetime(2016, 1, 2, 16)
# dt4 = datetime(2016, 1, 2, 17)
# dt5 = datetime(2016, 1, 2, 18)
#
# td = dt1 - dt2
# query_cnt = [dt1, dt2, dt3, dt4, dt5]
# print((dt5 - dt3).total_seconds())
# query_cnt = list(filter(lambda x: (dt5 - x).total_seconds() < 60 * 60 * 3, query_cnt))
#
# print(td.total_seconds())
