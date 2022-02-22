import sqlite3

# .db파일 만들기
con = sqlite3.connect("D:\\dev\\db_xingAPI\\kospi.db")

cursor = con.cursor()
# 테이블 만들기
# cursor.execute("CREATE TABLE kakao(Date text, Open int, High int, Low int, Closing int, Volume int)")
# record추가
cursor.execute("INSERT INTO kakao VALUES('16.06.03', 97000, 98600,96900,98000,321405)")
cursor.execute("INSERT INTO kakao VALUES('16.06.02', 96600, 97600,94900,97000,300000)")
cursor.execute("INSERT INTO kakao VALUES('16.06.02', 96600, 97600,94900,97000,300000)")

con.commit()
con.close()

con = sqlite3.connect("D:\\dev\\db_xingAPI\\kospi.db")

cursor.execute("SELECT * from kakao")
kakao = cursor.fetchall()
for i in kakao:
    print(i)

for r in kakao:
    print("")
    for c in r:
        print(c, end=" ")

import pandas as pd

ar = {'col1': [1, 2, 3, 4], 'col2': [10, 20, 30, 40], 'col3': [100, 200, 499, 999]}
df = pd.DataFrame(ar)

df.to_sql('test2', con, if_exists='replace')

# db로부터 df로 읽기
# df_from_db = pd.read_sql("select * from kakao", con, index_col=None)
# print(df_from_db)
