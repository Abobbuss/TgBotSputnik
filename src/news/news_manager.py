import os
import json
from pathlib import Path

class NewsManager:
    BASE_DIR = Path(__file__).parent
    IMAGES_DIR = BASE_DIR / "images"  # Папка с картинками
    JSON_DIR = BASE_DIR / "jsonNews"  # Папка с новостями

    def __init__(self):
        self.news_files = sorted(self.JSON_DIR.glob("*.json"), key=lambda x: int(x.stem))
        self.total_news = len(self.news_files)

    def get_news(self, index: int) -> dict | None:
        """Возвращает новость по индексу."""
        if 0 <= index < self.total_news:
            with open(self.news_files[index], "r", encoding="utf-8-sig") as file:
                news_data = json.load(file)
            return news_data

        return None
