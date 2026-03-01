import os
import asyncio
import shlex  # Untuk menangani karakter aneh di URL
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from utils.helpers import is_allowed, format_size

def get_url_from_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fungsi sakti untuk ambil link dari argumen ATAU reply"""
    # 1. Cek dari Reply
    if update.message.reply_to_message and update.message.reply_to_message.text:
        return update.message.reply_to_message.text.split()[0]
    # 2. Cek dari Argumen (/dls [link])
    if context.args:
        return context.args[0]
    return None

async def yts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return
    
    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Mana link-nya, Bos? Kirim linknya atau reply linknya pake perintah ini.")
        return

    msg = await update.message.reply_text("🎬 <b>YT-DLP:</b> Memproses link ke server...", parse_mode="HTML")
    
    # Gunakan shlex.quote agar karakter ? & / tidak bikin error
    safe_url = shlex.quote(url)
    
    try:
        # Kita pakai yt-dlp karena dia pintar cari link download asli di balik web
        cmd = f"yt-dlp -P {shlex.quote(str(DOWNLOAD_DIR))} -f 'bestvideo[height<=1080]+bestaudio/best' --merge-output-format mp4 {safe_url}"
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            await msg.edit_text("✅ <b>Youtube Selesai!</b> Kualitas Full HD disimpan di server.", parse_mode="HTML")
        else:
            await msg.edit_text(f"❌ <b>Gagal:</b> Link tidak valid atau tidak didukung.")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

async def dls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return
    
    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Kirim link atau reply link dengan /dls")
        return

    msg = await update.message.reply_text("⏳ <b>Aria2:</b> Menarik file ke server...", parse_mode="HTML")
    
    try:
        # Pakai Aria2 dengan tanda kutip agar aman dari karakter aneh
        safe_url = shlex.quote(url)
        cmd = f"aria2c -d {shlex.quote(str(DOWNLOAD_DIR))} --seed-time=0 {safe_url}"
        
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()
        
        await msg.edit_text("✅ <b>Selesai!</b> File sudah mendarat di storage server.", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ Gagal: {str(e)}")