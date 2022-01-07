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
