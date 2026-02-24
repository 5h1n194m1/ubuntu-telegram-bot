# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Path Utama
BASE_DIR = Path("/home/zul/zulbot")
TOKEN = os.getenv("TOKEN")

# User config - Mengambil dari .env, jika kosong pakai default ID kamu
raw_ids = os.getenv("ALLOWED_IDS", "1135391914,871102197,8036828631")
ALLOWED_IDS = {int(x.strip()) for x in raw_ids.split(",")} if raw_ids else {1135391914, 871102197, 8036828631}

# Owner ID - PERBAIKAN: Gunakan huruf kecil (int & os.getenv)
OWNER_ID = int(os.getenv("OWNER_ID", 1135391914))

# Storage paths
STORAGE_DIR = BASE_DIR / "storage"
DOWNLOAD_DIR = BASE_DIR / "downloads"

# Ensure directories exist (Membuat folder jika belum ada)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# File Paths
INFO_FILE = STORAGE_DIR / "info.txt"
LOG_FILE = STORAGE_DIR / "zul_download.log"

# Memastikan file ada (Jika belum ada akan dibuat kosong)
# touch(exist_ok=True) sudah cukup, tidak perlu cek .exists() lagi
INFO_FILE.touch(exist_ok=True)
LOG_FILE.touch(exist_ok=True)