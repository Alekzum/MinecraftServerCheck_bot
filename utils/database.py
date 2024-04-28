from utils.config import DATABASE_PATH
import sqlite3
import json


with sqlite3.connect('database.db') as con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS data (uid STRING PRIMARYKEY, host STRING, port INTEGER)")
    con.commit()


def get_raw() -> dict:
    with open(DATABASE_PATH, encoding="utf-8") as file:
        return json.load(file)


def set_host_port(uid: str, host: str, port: int):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO data VALUES (?, ?, ?)", (uid, host, port))
        con.commit()

def get_host_port(uid: str) -> tuple[str, int]:
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT host, port FROM data WHERE uid = ?", (uid, ))
        result = cur.fetchone()
    # print(result)
    return result

# print(get_raw())