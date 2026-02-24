# config/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path("/home/zul/zulbot")

TOKEN = os.getenv("TOKEN")

# User config
raw_ids = os.getenv("ALLOWED_IDS","")
ALLOWED_IDS = {int(x.strip()) for x in raw_ids.split(",")} if raw_ids else set()

# Owner ID keperluan notif khusus
OWNER_ID =INT(OS.GETENV("OWNER_ID", 1135391914))

# Storage paths
STORAGE_DIR = BASE_DIR / "storage"
DOWNLOAD_DIR = BASE_DIR / "downloads"

INFO_FILE = STORAGE_DIR / "info.txt"
LOG_FILE = STORAGE_DIR / "zul_download.log"

# Ensure directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

INFO_FILE.touch(exist_ok=True)
LOG_FILE.touch(exist_ok=True)

# memastikan file log & info selalu ada
if not INFO_FILE.exists():
    INFO_FILE.touch()
if not LOG_FILE.exists():
    LOG_FILE.touch()
