# -*-coding: utf-8 -*-

import win32com.client
import pythoncom
import os, sys

import pandas as pd
from pandas import DataFrame, Series, Panel


class XASessionEvents:
    상태 = False

    def OnLogin(self, code, msg):
        print("OnLogin : ", code, msg)
        XASessionEvents.상태 = True

    def OnLogout(self):
        print('--------------------')
        pass

    def OnDisconnect(self):
        print('=====================')
        pass


# user=tunan
# password=hn141437
# cert_passwd=
# host=demo.ebestsec.co.kr
# port=20001
# account=55501073968
# account_deriva=55551047139
# my=aaa

def Login(url='demo.ebestsec.co.kr', port=200001, svrtype=0, id='tunan', pwd='hn141437', cert=''):
    session = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEvents)
    session.SetMode("_XINGAPI7_", "TRUE")
    result = session.ConnectServer(url, port)

    if not result:
        nErrCode = session.GetLastError()
        strErrMsg = session.GetErrorMessage(nErrCode)
        return (False, nErrCode, strErrMsg, None, session)

    session.Login(id, pwd, cert, svrtype, 0)

    while XASessionEvents.상태 == False:
        pythoncom.PumpWaitingMessages()

    계좌 = []
    계좌수 = session.GetAccountListCount()

    for i in range(계좌수):
        계좌.append(session.GetAccountList(i))

    return (True, 0, "OK", 계좌, session)


if __name__ == "__main__":
    계좌정보 = pd.read_csv("secret/passwords.csv", converters={'계좌번호': str, '거래비밀번호': str})
    주식계좌정보 = 계좌정보.query("구분 == '거래'")
    if len(주식계좌정보) > 0:
        계좌번호 = 주식계좌정보['계좌번호'].values[0].strip()
        id = 주식계좌정보['사용자ID'].values[0].strip()
        pwd = 주식계좌정보['비밀번호'].values[0].strip()
        cert = 주식계좌정보['공인인증비밀번호'][0].strip()
        거래비밀번호 = 주식계좌정보['거래비밀번호'].values[0].strip()
        url = 주식계좌정보['url'][0].strip()

        result, code, msg, 계좌, session = Login(url=url, port=200001, svrtype=0, id=id, pwd=pwd, cert=cert)
        if result == False:
            sys.exit(0)

        for i in 계좌:
            print(i)
    else:
        print("secret디렉토리의 passwords.csv 파일에서 거래 계좌를 지정해 주세요")
