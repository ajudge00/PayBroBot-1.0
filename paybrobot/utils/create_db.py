import sqlite3

CONN = sqlite3.connect("../database.db")

with open("create_db.sql", "r") as f:
    sql = f.read()

CONN.executescript(sql)

CONN.commit()
CONN.close()