
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _parse_int_set(raw: str, fallback: set[int]) -> set[int]:
    values: set[int] = set()
    for part in (raw or "").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            values.add(int(part))
        except ValueError:
            continue
    return values or set(fallback)


TOKEN = (os.getenv("TOKEN") or "").strip() or None

_default_allowed = {1135391914, 871102197, 8036828631}
ALLOWED_IDS = _parse_int_set(os.getenv("ALLOWED_IDS", ""), _default_allowed) if os.getenv("ALLOWED_IDS") else set(_default_allowed)

try:
    OWNER_ID = int(os.getenv("OWNER_ID", str(next(iter(ALLOWED_IDS)))))
except (TypeError, ValueError):
    OWNER_ID = next(iter(ALLOWED_IDS))

STORAGE_DIR = BASE_DIR / "storage"
DOWNLOAD_DIR = BASE_DIR / "downloads"
INFO_FILE = STORAGE_DIR / "info.txt"
LOG_FILE = STORAGE_DIR / "zul_download.log"

MAX_TG_SIZE = int(os.getenv("MAX_TG_SIZE", str(49 * 1024 * 1024)))
DOWNLOAD_CONCURRENCY = max(1, int(os.getenv("DOWNLOAD_CONCURRENCY", "1")))

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

INFO_FILE.touch(exist_ok=True)
LOG_FILE.touch(exist_ok=True)
