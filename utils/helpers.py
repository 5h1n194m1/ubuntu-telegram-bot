from __future__ import annotations

import math
import re
import uuid
from pathlib import Path
from urllib.parse import unquote, urlparse

_URL_RE = re.compile(r"https?://[^\s<>]+")
_FILENAME_RE = re.compile(r'[^\w\-. ()\[\]]+', re.UNICODE)


def is_allowed(user_id, allowed_ids):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False

    try:
        return user_id in {int(x) for x in allowed_ids}
    except TypeError:
        return user_id == int(allowed_ids)


def format_size(size_bytes):
    try:
        size_bytes = float(size_bytes)
    except (TypeError, ValueError):
        return "0 B"

    if size_bytes <= 0:
        return "0 B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = min(int(math.floor(math.log(size_bytes, 1024))), len(size_name) - 1)
    p = math.pow(1024, i)
    s = size_bytes / p
    if s >= 100:
        formatted = f"{s:.0f}"
    elif s >= 10:
        formatted = f"{s:.1f}"
    else:
        formatted = f"{s:.2f}"
    return f"{formatted} {size_name[i]}"


def extract_first_url(text: str | None):
    if not text:
        return None
    match = _URL_RE.search(text)
    if not match:
        return None
    url = match.group(0).rstrip(").,]}>")
    url = url.rstrip("'\"")
    return url


def sanitize_filename(name: str, default: str = "download") -> str:
    name = unquote(name or "").strip()
    name = _FILENAME_RE.sub("_", name)
    name = re.sub(r"_+", "_", name).strip("._ ")
    return name or default


def filename_from_url(url: str, default: str = "download.bin") -> str:
    parsed = urlparse(url)
    base = Path(parsed.path).name
    if not base:
        return default
    base = sanitize_filename(base, default=default)
    return base or default


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)


def unique_token(length: int = 8) -> str:
    return uuid.uuid4().hex[:length]


async def update_status_message(msg, text, parse_mode=None):
    try:
        await msg.edit_text(text, parse_mode=parse_mode)
    except Exception:
        pass
