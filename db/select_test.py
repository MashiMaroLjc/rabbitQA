# coding:utf-8
import sqlite3
keyword = "女朋友"
sql = "select * from qa_pair where QUESTION like \'%{}%\' and QUESTION like \'%{}%\'".format(keyword,"妈妈")

conn = sqlite3.connect('qa.db')
cursor = conn.cursor()
result = cursor.execute(sql)
for row in result:
    print(row)
