import sqlite3
import os
import sys
def initialize_database():

    

    
    if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
    else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(base_path, "computers.db")
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Таблица компьютеров с уникальностью по имени
    cur.execute("""
    CREATE TABLE IF NOT EXISTS computers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        ip TEXT,
        mac TEXT,
        os_full TEXT,
        user TEXT,
        dst TEXT,
        address TEXT,
        admin TEXT,
        arm_type TEXT,
        device_type TEXT
    )
    """)

    # Добавляем колонку serial_number, если её нет
    try:
        cur.execute("ALTER TABLE computers ADD COLUMN serial_number TEXT")
    except sqlite3.OperationalError:
        # колонка уже существует
        pass

    # Остальные таблицы
    cur.execute("""
    CREATE TABLE IF NOT EXISTS network_interfaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        computer_id INTEGER,
        type TEXT,
        ip TEXT,
        mac TEXT,
        mask TEXT,
        FOREIGN KEY(computer_id) REFERENCES computers(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS disks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        computer_id INTEGER,
        name TEXT,
        serial TEXT,
        size INTEGER,
        FOREIGN KEY(computer_id) REFERENCES computers(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS dst (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    conn.commit()
    conn.close()
