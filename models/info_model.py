
from __future__ import annotations

from pathlib import Path

from config.settings import INFO_FILE


class InfoModel:
    @staticmethod
    def get_info():
        path = Path(INFO_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            return "<b>ZUL SERVER INFO</b>\nBelum ada informasi yang diset. Gunakan /setinfo untuk mengisi."

        content = path.read_text(encoding="utf-8")
        content = content.strip()
        if not content:
            return "<b>ZUL SERVER INFO</b>\nBelum ada informasi yang diset. Gunakan /setinfo untuk mengisi."
        return content

    @staticmethod
    def set_info(text):
        path = Path(INFO_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
