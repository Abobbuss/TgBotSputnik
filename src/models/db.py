import sqlite3

from typing import Optional, Any


class Database:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self._ensure_db_initialized()

    def _connect(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def _ensure_db_initialized(self):
        with self._connect() as db:
            cursor = db.cursor()

            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    phone TEXT,
                    referral_name TEXT,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица рефералов (общее количество)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Referrals (
                    ref_name TEXT PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 0
                )
            ''')

            # Привязка пользователей к рефералам
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ReferralUsers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ref_name TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ref_name) REFERENCES Referrals(ref_name),
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                )
            ''')

            # Таблица действий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UserActions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    info TEXT,
                    action_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                )
            ''')

            db.commit()


    def user_exists(self, telegram_id: int) -> bool:
        """
        Проверяет, существует ли пользователь с таким telegram_id.
        """
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM Users WHERE telegram_id = ?", (telegram_id,))
            return cursor.fetchone() is not None


    def add_user(self, telegram_id: int, referral_name: Optional[str] = None, username: Optional[str] = None):
        """
        Добавляет пользователя. Если передан реферал — увеличивает его счётчик и добавляет связь.
        Не добавляет, если пользователь уже есть.
        """
        with self._connect() as db:
            cursor = db.cursor()

        if self.user_exists(telegram_id):
            return

        cursor.execute(
                "INSERT OR IGNORE INTO Users (telegram_id, referral_name, username) VALUES (?, ?, ?)",
                (telegram_id, referral_name, username)
            )

        if referral_name:
            cursor.execute("INSERT OR IGNORE INTO Referrals (ref_name, count) VALUES (?, 0)", (referral_name,))
            cursor.execute("UPDATE Referrals SET count = count + 1 WHERE ref_name = ?", (referral_name,))
            cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (telegram_id,))
            user_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO ReferralUsers (ref_name, user_id) VALUES (?, ?)", (referral_name, user_id))

        db.commit()


    def update_user_info(self, telegram_id: int, **kwargs: Any):
        """
        Обновляет произвольные поля пользователя по telegram_id.
        Если поле info уже заполнено, то новое значение добавляется к нему через пробел.
        """
        if not kwargs:
            return

        with self._connect() as db:
            cursor = db.cursor()

            if "info" in kwargs:
                cursor.execute("SELECT info FROM Users WHERE telegram_id = ?", (telegram_id,))
                existing_info = cursor.fetchone()
                if existing_info and existing_info[0]:
                    kwargs["info"] = existing_info[0].strip() + "\n" + kwargs["info"].strip()

            fields = ', '.join(f"{k} = ?" for k in kwargs)
            values = list(kwargs.values())
            values.append(telegram_id)

            cursor.execute(f"UPDATE Users SET {fields} WHERE telegram_id = ?", values)
            db.commit()


    def has_phone(self, telegram_id: int) -> bool:
        """
        Проверяет, указан ли номер телефона у пользователя.
        """
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT phone FROM Users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            return bool(result and result[0])

    def add_user_action(self, telegram_id: int, action: str, info: Optional[str] = None):
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (telegram_id,))
            result = cursor.fetchone()
            if not result:
                return
            user_id = result[0]
            cursor.execute(
                "INSERT INTO UserActions (user_id, action, info) VALUES (?, ?, ?)",
                (user_id, action, info)
            )
            db.commit()

    def get_all_user_actions(self):
        """
        Возвращает список всех действий пользователей с информацией и временем.
        """
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute('''
                SELECT Users.telegram_id, Users.username, Users.phone,
                       Actions.info, Actions.action, Actions.action_time
                FROM UserActions AS Actions
                LEFT JOIN Users ON Users.id = Actions.user_id
                ORDER BY Actions.action_time DESC
            ''')
            return cursor.fetchall()


    def get_all_referrals(self):
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT ref_name, count FROM Referrals ORDER BY count DESC")
            return cursor.fetchall()


    def get_user_actions_by_telegram_id(self, telegram_id: int) -> list[str]:
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT action FROM UserActions
                WHERE user_id = (SELECT id FROM Users WHERE telegram_id = ?)
            """, (telegram_id,))
            return [row[0] for row in cursor.fetchall()]


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


    def get_users_by_ref(self, ref_name: str):
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute('''
                SELECT Users.telegram_id, Users.username, Users.registration_date
                FROM ReferralUsers
                LEFT JOIN Users ON Users.id = ReferralUsers.user_id
                WHERE ReferralUsers.ref_name = ?
                ORDER BY Users.registration_date DESC
            ''', (ref_name,))
            return cursor.fetchall()


    def get_last_demo_info(self, telegram_id: int) -> Optional[str]:
        with self._connect() as db:
            cursor = db.cursor()
            cursor.execute("""
                SELECT Actions.info
                FROM UserActions AS Actions
                JOIN Users ON Users.id = Actions.user_id
                WHERE Users.telegram_id = ?
                  AND Actions.action LIKE 'Запись на демо%'
                ORDER BY Actions.action_time DESC
                LIMIT 1
            """, (telegram_id,))
            result = cursor.fetchone()
            return result[0] if result and result[0] else None