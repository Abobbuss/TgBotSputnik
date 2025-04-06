import sqlite3
from pathlib import Path
from typing import Optional, Any


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._ensure_db_initialized()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db_initialized(self):
        with self._connect() as db:
            cursor = db.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    email TEXT,
                    name TEXT,
                    company TEXT,
                    position TEXT,
                    referral_name TEXT,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Referrals (
                    ref_name TEXT PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UserActions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    action_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (telegram_id) REFERENCES Users(telegram_id)
                )
            ''')

            db.commit()

    def add_user(self, telegram_id: int, referral_name: Optional[str] = None):
        """
        Добавляет пользователя. Если передан реферал — увеличивает его счётчик.
        """
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO Users (telegram_id, referral_name) VALUES (?, ?)",
                (telegram_id, referral_name)
            )
            db.commit()

            if referral_name:
                cursor.execute("INSERT OR IGNORE INTO Referrals (ref_name, count) VALUES (?, 0)", (referral_name,))
                cursor.execute("UPDATE Referrals SET count = count + 1 WHERE ref_name = ?", (referral_name,))
                db.commit()

    def update_user_info(self, telegram_id: int, **kwargs: Any):
        """
        Обновляет произвольные поля пользователя по telegram_id.
        """
        if not kwargs:
            return

        fields = ', '.join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values())
        values.append(telegram_id)

        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute(f"UPDATE Users SET {fields} WHERE telegram_id = ?", values)
            db.commit()

    def add_user_action(self, telegram_id: int, action: str):
        """
        Добавляет новую запись о действии пользователя.
        """
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO UserActions (telegram_id, action) VALUES (?, ?)",
                (telegram_id, action)
            )
            db.commit()

    def get_all_user_actions(self):
        """
        Возвращает список всех действий пользователей.
        """
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute('''
                SELECT Users.telegram_id, Users.name, Users.email, Users.company, Users.position, 
                       Actions.action, Actions.action_time
                FROM UserActions AS Actions
                LEFT JOIN Users ON Users.telegram_id = Actions.telegram_id
                ORDER BY Actions.action_time DESC
            ''')
            return cursor.fetchall()

    def get_all_referrals(self):
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT ref_name, count FROM Referrals ORDER BY count DESC")
            return cursor.fetchall()

    def get_user(self, telegram_id: int):
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users WHERE telegram_id = ?", (telegram_id,))
            return cursor.fetchone()

    def get_all_users(self):
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users ORDER BY registration_date DESC")
            return cursor.fetchall()
