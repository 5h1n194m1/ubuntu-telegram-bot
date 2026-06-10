
import logging
import os
import sys

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from config.settings import TOKEN
from controllers.info_controller import info, setinfo
from controllers.system_controller import (
    cleanup,
    cleanup_callback,
    list_files,
    manage_files,
    start,
    status,
    storage,
    temp,
)
from controllers.download_controller import dl, dls, yt, yts
from models.system_model import SystemModel

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

HIJAU_BOLD = "\033[1;32m"
RESET = "\033[0m"


def get_terminal_banner():
    temp_value = SystemModel.get_cpu_temp()
    hostname = SystemModel.get_hostname()

    banner = f"""{HIJAU_BOLD}
------------------------------------------------
🚀 ZULBOT:
   Bot     : ✅ ACTIVE
   Suhu CPU : {temp_value}
   Hostname : {hostname}
------------------------------------------------

  ███████╗██╗   ██╗██╗
  ╚══███╔╝██║   ██║██║
    ███╔╝ ██║   ██║██║
   ███╔╝  ██║   ██║██║
  ███████╗╚██████╔╝███████╗
  ╚══════╝ ╚═════╝ ╚══════╝

Status: Online & Ready
------------------------------------------------{RESET}
"""
    return banner


async def error_handler(update, context):
    logging.exception("Unhandled error in bot", exc_info=context.error)


def main():
    if not TOKEN:
        print(f"{HIJAU_BOLD}❌ ERROR: TOKEN tidak ditemukan!{RESET}")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("temp", temp))
    app.add_handler(CommandHandler("storage", storage))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("cleanup", cleanup))
    app.add_handler(CommandHandler("manage", manage_files))
    app.add_handler(CallbackQueryHandler(cleanup_callback))

    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("setinfo", setinfo))

    app.add_handler(CommandHandler("dl", dl))
    app.add_handler(CommandHandler("yt", yt))
    app.add_handler(CommandHandler("dls", dls))
    app.add_handler(CommandHandler("yts", yts))

    app.add_error_handler(error_handler)

    if sys.stdin.isatty():
        os.system("clear")
        print(get_terminal_banner())
    else:
        print(f"{HIJAU_BOLD}🚀 ZULBOT ACTIVE - Host: {SystemModel.get_hostname()} | Temp: {SystemModel.get_cpu_temp()}{RESET}")

    app.run_polling()


if __name__ == "__main__":
    main()
