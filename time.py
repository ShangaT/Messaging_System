import time, datetime
import sqlite3

db = sqlite3.connect("Users.db") #подключаемся к базе данных

def Delete_db(fromm, value):
    db = sqlite3.connect("Users.db")
    db.row_factory = lambda cursor, row: row[0]
    db_req = f"DELETE FROM {fromm} WHERE time < '{value}';"
    db_value = db.cursor().execute(db_req)
    db.commit()

while True: #бесконечный цикл с задержкой в один день, для удаления учетных записей и сообщений
    #time.sleep(86400)
    time.sleep(10)
    time_now = datetime.datetime.now()
    Delete_db('users', time_now)
    Delete_db('secrets', time_now)
