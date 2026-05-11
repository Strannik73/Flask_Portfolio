import sqlite3
from datetime import datetime


# создание таблицы
def init_logs_db():

    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT,
            date TEXT,
            time TEXT,
            action TEXT,
            result TEXT
        )
    """)

    conn.commit()
    conn.close()


# запись логов
def log_event(login, action, result):

    now = datetime.now()

    date = now.strftime("%d.%m.%Y")
    time = now.strftime("%H:%M:%S")

    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (login, date, time, action, result)
        VALUES (?, ?, ?, ?, ?)
    """, (login, date, time, action, result))

    conn.commit()
    conn.close()