import os
from pathlib import Path

class PresentationManager:
    PRESENTATION_DIR = Path(__file__).parent.parent / "latest_presentations"

    @classmethod
    def get_latest_presentation(cls) -> Path | None:
        """Возвращает путь к последней презентации (по дате изменения файла)."""
        if not cls.PRESENTATION_DIR.exists():
            return None

        files = sorted(cls.PRESENTATION_DIR.glob("*.pptx"), key=lambda x: x.stat().st_mtime, reverse=True)
        return files[0] if files else None
