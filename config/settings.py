# config/settings.py
# Semua konfigurasi & path dipusatkan di sini

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path("/home/zul/zulbot")

TOKEN = os.getenv("TOKEN")

# User config
ALLOWED_IDS = {1135391914, 871102197, 8036828631}
OWNER_ID = {1135391914, 871102197}

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
