import win32com.client
import pythoncom
import sys
import time
import configparser

XING_PATH = "C:\\eBest\\xingAPI"
TODAY = time.strftime("%Y%m%d")
TODAY_TIME = time.strftime("%H%M%S")
TODAY_S = time.strftime("%Y-%m-%d")


class XASessionEventHandler:
    login_state = 0

    def OnLogin(self, code, msg):
        print("on login start")

        if code == "0000":
            print("login sucess")
            XASessionEventHandler.login_state = 1
        else:
            XASessionEventHandler.login_state = -1
            print("login fail")


class XAQueryEventHandler:
    query_state = 0
    query_code = ''
    T1102_query_state = 0
    T8413_query_state = 0

    def OnReceiveData(self, code):
        XAQueryEventHandler.query_code = code
        XAQueryEventHandler.query_state = 1


def login(mode="DEMO"):
    instXASession = win32com.client.DispatchWithEvents("XA_Session.XASession", XASessionEventHandler)

    run_mode = "EBEST_" + mode
    config = configparser.ConfigParser()
    config.read('D:\\dev\python\\xingAPI\\stocklab\\agent\\conf\\config.ini')

    user = config[run_mode]['user']
    passwd = config[run_mode]['password']
    cert_passwd = config[run_mode]['cert_passwd']
    host = config[run_mode]['host']
    port = config[run_mode]['port']
    account = config[run_mode]['account']
    account_deriva = config[run_mode]['account_deriva']

    instXASession.ConnectServer(host, port)
    instXASession.Login(user, passwd, cert_passwd, 0, 0)
    while XASessionEventHandler.login_state == 0:
        pythoncom.PumpWaitingMessages()

    login = XASessionEventHandler.login_state
    return login


def wait_for_event(code):
    while XAQueryEventHandler.query_state == 0:
        pythoncom.PumpWaitingMessages()

    if XAQueryEventHandler.query_code != code:
        print('different code')
        return 0

    XAQueryEventHandler.query_state = 0
    XAQueryEventHandler.query_code = ''
    return 1


def get_8432():
    """코스피 지수 선물 마스터 조회"""
    tr_code = 't8432'
    INBLOCK = f"{tr_code}InBlock"
    INBLOCK1 = f"{tr_code}InBlock1"
    OUTBLOCK = f"{tr_code}OutBlock"
    OUTBLOCK1 = f"{tr_code}OutBlock1"
    OUTBLOCK2 = f"{tr_code}OutBlock2"
    OUTBLOCK3 = f"{tr_code}OutBlock3"

    query = win32com.client.DispatchWithEvents('XA_DataSet.XAQuery', XAQueryEventHandler)
    query.ResFileName = "C:\\eBest\\xingAPI\\Res\\" + tr_code + ".res"
    query.SetFieldData(INBLOCK, 'gubun', 0, "1")  # 코스피200 지수선물 마스터 조회
    # 구분
    # V: 변동성지수선물
    # S: 섹터지수선물
    # 그 이외의 값은 코스피200지수선물
    query.Request(0)

    ret = wait_for_event(tr_code)  # Query event의 state가 1이 될때까지 기다림, query event가 제대로 끝가지 않을시 0 리턴

    if ret == 0:
        return [{'error': {'message': tr_code + 'msg error'}}]

    result1 = []
    nCount = query.GetBlockCount(OUTBLOCK)

    for i in range(nCount):
        sh_code = query.GetFieldData(OUTBLOCK, 'shcode', i).strip()  # 종목코드
        sh_name = query.GetFieldData(OUTBLOCK, 'hname', i).strip()  # 종목명
        lst = {'code': sh_code, 'name': sh_name}
        result1.append(lst)

    return result1


def get_2301(yyyymm):
    """옵션 전광판"""
    tr_code = 't2301'


def get_0441():
    """선물옵션 보유종목 조회"""
    tr_code = 't0441'
    INBLOCK = f"{tr_code}InBlock"
    INBLOCK1 = f"{tr_code}InBlock1"
    OUTBLOCK = f"{tr_code}OutBlock"
    OUTBLOCK1 = f"{tr_code}OutBlock1"
    OUTBLOCK2 = f"{tr_code}OutBlock2"
    OUTBLOCK3 = f"{tr_code}OutBlock3"

    deriva_acc = '55551047139'
    passwd = 'hn141437'

    query = win32com.client.DispatchWithEvents("XA_DataSet.XAQuery", XAQueryEventHandler)
    query.ResFileName = "C:\\eBest\\xingAPI\\Res\\" + tr_code + ".res"
    query.SetFieldData(INBLOCK, 'accno', 0, deriva_acc)
    query.SetFieldData(INBLOCK, 'passwd', 0, passwd)
    query.SetFieldData(INBLOCK, 'cts_expcode', 0, '')
    query.SetFieldData(INBLOCK, 'cts_medocd', 0, '')
    query.Request(0)

    ret = wait_for_event(tr_code)

    if ret == 0:
        return [{'error': {'message': tr_code + 'msg error'}}]

    result = []
    result2 = []

    trade_profit = query.GetFieldData(OUTBLOCK, 'tdtsunik', 0).strip()  # 매매손익합
    total_value = query.GetFieldData(OUTBLOCK, 'tappamt', 0).strip()  # 평가금액
    value_profit = query.GetFieldData(OUTBLOCK, 'tsunik', 0).strip()  # 평가손익
    lst = {'trade_profit': trade_profit, 'total_value': total_value, 'value_profit': value_profit}
    result.append(lst)

    nCount = query.GetBlockCount(OUTBLOCK1)

    for i in range(nCount):
        code = query.GetFieldData(OUTBLOCK1, 'expcode', i).strip()  # 종목코드
        buy_sell = query.GetFieldData(OUTBLOCK1, 'medosu', i).strip()  # 매도/매수
        qty = query.GetFieldData(OUTBLOCK1, 'jqty', i).strip()  # quantity
        orderable_qty = query.GetFieldData(OUTBLOCK1, 'cqty', i).strip()  # 청산가능수량
        buy_sell_add = query.GetFieldData(OUTBLOCK1, 'medocd', i).strip()  # 매매코드, 구분
        trade_profit = query.GetFieldData(OUTBLOCK1, 'dtsunik', i).strip()  # 매매손
        price = query.GetFieldData(OUTBLOCK1, 'price', i).strip()  # 현재가
        value_profit = query.GetFieldData(OUTBLOCK1, 'dtsunik1', i).strip()  # 평가손익
        lst = {'code': code, 'buy_sell': buy_sell, 'qty': float(qty), 'orderable_qty': float(orderable_qty),
               'buy_sell_add': buy_sell_add, 'trade_profit': float(trade_profit), 'price': float(price),
               'value_profit': value_profit}

        result2.append(lst)

    result.append(result2)
    return result


if __name__ == '__main__':
    ret = login("DEMO")
    if ret == 0:
        print('fail to login')
        quit(0)
    time.sleep(1)

    print('최근월 선물 조회')
    rest = get_8432()
    if 'error' in rest[0]:
        print(rest[0]['error']['message'])
    for each in rest:
        print(each)

    # 선옵 계좌조회
    print('---account balance---')
    cur_hold = get_0441()
    total = cur_hold[0]

    print('trade_profit : ', total['trade_profit'])
    print('value profit: ', total['value_profit'])
    print('MtM: ', total['total_value'])

    print('상품별 손익')
    print(f"{'코드':<10}{'수량':<10}{'매수/매도':<10}",
          f"{'가격':<10}{'매매손익':<10}{'평가손익':<10}")
    for each in cur_hold[1]:
        print(f"{each['code']:<10}{each['qty']:<10}{each['buy_sell']:<10}",
              f"{each['price']:<10}{each['trade_profit']:<10}{each['value_profit']:<10}")
