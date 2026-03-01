# app.py
import os
import logging
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config.settings import TOKEN

# Models & Controllers
from models.system_model import SystemModel
from controllers.system_controller import (
    start, status, storage, list_files, cleanup, cleanup_callback, manage_files)
from controllers.info_controller import info, setinfo
from controllers.download_controller import dl, yt, dls, yts

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.WARNING
)

# Warna ANSI untuk Terminal (Green Style)
HIJAU_BOLD = "\033[1;32m"
RESET = "\033[0m"

def get_terminal_banner():
    """Menghasilkan banner ASCII berwarna hijau dengan spek Toshiba Satellite C640."""
    temp = SystemModel.get_cpu_temp()
    hostname = SystemModel.get_hostname()
    
    banner = f"""{HIJAU_BOLD}
------------------------------------------------
🚀 Zul Terminal Info:
   Zul Bot  : ✅ ACTIVE
   Suhu CPU : {temp}
   Hostname : {hostname}
------------------------------------------------

  ███████╗██╗   ██╗██╗     
  ╚══███╔╝██║   ██║██║     
    ███╔╝ ██║   ██║██║     
   ███╔╝  ██║   ██║██║     
  ███████╗╚██████╔╝███████╗
  ╚══════╝ ╚═════╝ ╚══════╝

Selamat Datang, Dzulfikar!
Server: Toshiba Satellite C640 (i5-2450M)
Spek  : RAM 8GB DDR3 | HDD 320GB | OS: Ubuntu 25.10
Status: Online & Ready
------------------------------------------------{RESET}
"""
    return banner

def main():
    if not TOKEN:
        print(f"{HIJAU_BOLD}❌ ERROR: TOKEN tidak ditemukan!{RESET}")
        return

    # Inisialisasi Application
    app = ApplicationBuilder().token(TOKEN).build()

    # [1] Register System Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("storage", storage))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("cleanup", cleanup))
    app.add_handler(CommandHandler("manage", manage_files))  
    app.add_handler(CallbackQueryHandler(cleanup_callback))
    
    # [2] Register Info Handlers
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("setinfo", setinfo))
    
    # [3] Register Download Handlers
    app.add_handler(CommandHandler("dl", dl))   
    app.add_handler(CommandHandler("yt", yt))   
    app.add_handler(CommandHandler("dls", dls)) 
    app.add_handler(CommandHandler("yts", yts)) 

    # Tampilan Startup
    if sys.stdin.isatty():
        os.system('clear')
        print(get_terminal_banner())
    else:
        # Tampilan hijau untuk log systemd (journalctl)
        print(f"{HIJAU_BOLD}🚀 ZUL BOT ACTIVE - Server: {SystemModel.get_hostname()} (i5-2450M) | Temp: {SystemModel.get_cpu_temp()}{RESET}")

    # Jalankan Bot
    app.run_polling()

if __name__ == "__main__":
    main()