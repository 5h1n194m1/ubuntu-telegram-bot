import os
import asyncio
import shlex
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from utils.helpers import is_allowed

def get_url_from_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.text:
        return update.message.reply_to_message.text.split()[0]
    if context.args:
        return context.args[0]
    return None

# Fungsi 'dl' yang dicari app.py
async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await dls(update, context)

# Fungsi 'yt' yang dicari app.py
async def yt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await yts(update, context)

async def dls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return
    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Kirim/Reply link dulu, Bos.")
        return
    msg = await update.message.reply_text("⏳ <b>Aria2:</b> Memproses...", parse_mode="HTML")
    try:
        safe_url = shlex.quote(url)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        cmd = f"aria2c -d {shlex.quote(str(DOWNLOAD_DIR))} --seed-time=0 {safe_url}"
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()
        await msg.edit_text("✅ <b>Selesai!</b> File masuk storage server.", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

async def yts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return
    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Mana link YouTube-nya?")
        return
    msg = await update.message.reply_text("🎬 <b>YT-DLP:</b> Sedang menyedot video...", parse_mode="HTML")
    try:
        safe_url = shlex.quote(url)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        cmd = f"yt-dlp -P {shlex.quote(str(DOWNLOAD_DIR))} -f 'best' --merge-output-format mp4 {safe_url}"
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()
        await msg.edit_text("✅ <b>Youtube Berhasil!</b>", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")