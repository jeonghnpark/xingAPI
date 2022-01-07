import sqlite3

con = sqlite3.connect("D:\\dev\\db_xingAPI\\kospi.db")

cursor = con.cursor()

import pandas as pd

ar = {'col1': [1, 2, 3, 4], 'col2': [10, 20, 30, 40], 'col3': [100, 200, 499, 999]}
df = pd.DataFrame(ar)

df.to_sql('test2', con, if_exists='replace')

# db로부터 df로 읽기
# df_from_db = pd.read_sql("select * from kakao", con, index_col=None)
# print(df_from_db)
