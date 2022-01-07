import sqlite3

con = sqlite3.connect("D:\\dev\\db_xingAPI\\kospi.db")

cursor = con.cursor()
cursor.execute("SELECT * from kakao")
kakao = cursor.fetchall()
for i in kakao:
    print(i)

for r in kakao:
    print("")
    for c in r:
        print(c, end=" ")
