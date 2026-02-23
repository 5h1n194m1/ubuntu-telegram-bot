"""
Main Entry Point - ZULBOT MVC
"""

import os
import requests
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.ext import ContextTypes
from config.settings import TOKEN
from models.system_model import SystemModel
from controllers.system_controller import start, status, storage, list_files, cleanup
from controllers.info_controller import info, setinfo
from controllers.download_controller import dl, yt
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from utils.helpers import is_allowed

# Logging setup (Level WARNING agar terminal tidak penuh log sampah)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.WARNING 
)

def get_terminal_banner():
    # Ambil suhu dan data lainnya
    temp = SystemModel.get_cpu_temp()
    
    # Gunakan print satu per satu baris agar tidak terpotong di log journalctl
    banner = [
        "------------------------------------------------",
        "🚀 Zul Terminal Info:",
        "   Zul Bot : ✅ JALAN",
        f"   Suhu CPU: {temp}",
        "------------------------------------------------",
        "",
        "  ███████╗██╗   ██╗██╗     ",
        "  ╚══███╔╝██║   ██║██║     ",
        "    ███╔╝ ██║   ██║██║     ",
        "   ███╔╝  ██║   ██║██║     ",
        "  ███████╗╚██████╔╝███████╗",
        "  ╚══════╝ ╚═════╝ ╚══════╝",
        "",
        "Selamat Datang, Dzulfikar!",
        "Server: Ubuntu i3-2330M | Status: Online",
        "------------------------------------------------"
    ]
    return "\n".join(banner)

def main():
    if not TOKEN:
        print("❌ ERROR: BOT_TOKEN tidak ditemukan di .env")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Register Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("storage", storage))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("cleanup", cleanup))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("setinfo", setinfo))
    app.add_handler(CommandHandler("dl", dl))
    app.add_handler(CommandHandler("yt", yt))

    # Tampilkan Banner Keren
    # os.system('clear') # Biar terminal bersih
    # print(get_terminal_banner())
    
    import sys
    if sys.stdin.isatty(): # Cek apakah dijalankan manual di terminal
        os.system('clear')
        print(get_terminal_banner())
    else:
        # Jika jalan sebagai service, cukup print info singkat ke log
        print("🚀 ZulBot MVC Started in Background Mode")
        print("------------------------------------------------")
        print(f"🚀 ZUL BOT MVC IS ACTIVE")
        print(f"📡 Server   : {SystemModel.get_hostname()}")
        print(f"🔥 CPU Temp : {SystemModel.get_cpu_temp()}")
        print("------------------------------------------------")

    app.run_polling()

# ==========================================
# 1. DOWNLOAD KE SERVER (STORAGE)
# ==========================================



if __name__ == "__main__":
    main()