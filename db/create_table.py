import sqlite3
con = sqlite3.connect('qa.db')
delete_table = "DROP TABLE qa_pair;"
create_table = """
CREATE TABLE qa_pair(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    QUESTION TEXT NOT NULL,
    ANSWER TEXT NOT NULL
);
"""
con.execute(delete_table)
con.execute(create_table)
con.commit()
con.close()

