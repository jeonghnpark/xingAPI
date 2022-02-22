import win32com.client

client = win32com.client.Dispatch("XA_Session.XASession")
client.ConnectServer("demo.ebestsec.co.kr", 20001)
print(client)
# client.DisconnectServer()

import time
from datetime import datetime

# , timedelta

# from datetime.timedelta import total_seconds

# print(datetime.today())

# print((datetime.today() - 3).total_second())

dt1 = datetime(2016, 1, 2, 14)
dt2 = datetime(2016, 1, 2, 15)
dt3 = datetime(2016, 1, 2, 16)
dt4 = datetime(2016, 1, 2, 17)
dt5 = datetime(2016, 1, 2, 18)

td = dt1 - dt2
query_cnt = [dt1, dt2, dt3, dt4, dt5]
print((dt5 - dt3).total_seconds())
query_cnt = list(filter(lambda x: (dt5 - x).total_seconds() < 60 * 60 * 3, query_cnt))

print(td.total_seconds())
