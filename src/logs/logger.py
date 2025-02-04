import os
from datetime import datetime
import asyncio
import threading
import logging


class Logger:
    def __init__(self, log_dir="logs"):
        """
        Инициализация логгера.

        Args:
            log_dir (str): Путь к папке для хранения логов.
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)    # Создаём папку для логов, если её нет
        self.lock = threading.Lock()                # Для потокобезопасности

    def _get_log_file(self):
        """
        Возвращает путь к файлу логов с текущей датой.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{current_date}.log")

        return log_file

    def _write_log(self, level, message):
        """
        Общая функция для записи логов.

        Args:
            level (str): Уровень лога ("INFO" или "ERROR").
            message (str): Сообщение для записи.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{level}] {timestamp} - {message}\n"

        with self.lock:
            with open(self._get_log_file(), "a", encoding="utf-8") as log_file:
                log_file.write(log_message)

    def info(self, message):
        """
        Записывает сообщение с уровнем INFO.

        Args:
            message (str): Сообщение для записи.
        """
        logging.info(message)
        self._write_log("INFO", message)

    def error(self, message):
        """
        Записывает сообщение с уровнем ERROR.

        Args:
            message (str): Сообщение для записи.
        """
        logging.error(message)
        self._write_log("ERROR", message)

