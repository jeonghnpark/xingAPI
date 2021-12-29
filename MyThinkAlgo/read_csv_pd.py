import pandas as pd

account_info = pd.read_csv("pass.csv", converters={'계좌번호': str})
acc1 = account_info.query("구분=='거래'")
