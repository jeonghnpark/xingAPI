import os, re, sys, time, pytz
import pandas as pd
from getpass import getpass
from datetime import datetime, timedelta
from pprint import pprint

if sys.platform == 'win32':
    from win32com.client import DispatchWithEvents
    from pythoncom import PumpWaitingMessages
else:
    raise Exception('xingAPI는 윈도우 환경에서만 사용 가능합니다')

MYNAME = 't12321'
IN = "%sInBlock" % MYNAME

print(IN)
