import sqlite3
import json
import glob

con = sqlite3.connect('qa.db')

print("insert the web text...")
file = glob.glob("./web*.json")
for fp in file:
    print("######### Deal File...", fp)
    for line in open(fp, "r", encoding="utf-8"):
        line = line.strip()
        item = json.loads(line)
        sql = "INSERT INTO qa_pair (QUESTION,ANSWER) VALUES (\"{}\",\"{}\");".format(item["title"], item["content"])
        print("execute sql:", sql)
        con.execute(sql)
    con.commit()

print("insert the baike...")
file = glob.glob("./baike*.json")
for fp in file:
    print("######### Deal File...", fp)
    for line in open(fp, "r", encoding="utf-8"):
        line = line.strip()
        item = json.loads(line)
        sql = "INSERT INTO qa_pair (QUESTION,ANSWER) VALUES (\"{}\",\"{}\");".format(item["title"], item["answer"])
        print("execute sql:", sql)
        con.execute(sql)
    con.commit()