import os
import asyncio
import shlex
import glob
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from utils.helpers import is_allowed, format_size

MAX_TG_SIZE = 49 * 1024 * 1024 

def get_url_from_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.text:
        return update.message.reply_to_message.text.split()[0]
    if context.args:
        return context.args[0]
    return None

async def dls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return
    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Kirim/Reply link-nya dulu, Bos.")
        return
    
    msg = await update.message.reply_text("⏳ <b>Aria2:</b> Men-download ke server...", parse_mode="HTML")
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        filename = f"dl_{update.effective_user.id}_{int(asyncio.get_event_loop().time())}"
        path = os.path.join(DOWNLOAD_DIR, filename)
        
        cmd = f"aria2c -d {shlex.quote(str(DOWNLOAD_DIR))} -o {shlex.quote(filename)} --seed-time=0 {shlex.quote(url)}"
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()

        if os.path.exists(path):
            file_size = os.path.getsize(path)
            
            # CEK UKURAN FILE
            if file_size < MAX_TG_SIZE:
                await msg.edit_text(f"📤 <b>Selesai!</b> Mengirim file ({format_size(file_size)})...", parse_mode="HTML")
                with open(path, 'rb') as f:
                    await update.message.reply_document(document=f)
            else:
                await msg.edit_text(
                    f"📦 <b>Selesai!</b>\n"
                    f"Ukuran file: <b>{format_size(file_size)}</b> (Melebihi 49MB).\n"
                    f"File tetap disimpan di server Toshiba.\n"
                    f"Gunakan <code>/list</code> atau WinSCP untuk mengambilnya.", 
                    parse_mode="HTML"
                )
        else:
            await msg.edit_text("❌ Gagal: File tidak ditemukan setelah download.")
            
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

async def yts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return
    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Link YouTube-nya mana?")
        return

    msg = await update.message.reply_text("🎬 <b>YT-DLP:</b> Sedang memproses video...", parse_mode="HTML")
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        output_template = os.path.join(DOWNLOAD_DIR, f"yt_{update.effective_user.id}_%(title)s.%(ext)s")
        
        # Download kualitas terbaik tapi usahakan mp4
        cmd = f"yt-dlp -o {shlex.quote(output_template)} -f 'best[ext=mp4]/best' {shlex.quote(url)}"
        process = await asyncio.create_subprocess_shell(cmd)
        await process.wait()

        search_pattern = os.path.join(DOWNLOAD_DIR, f"yt_{update.effective_user.id}_*")
        files = glob.glob(search_pattern)

        if files:
            video_path = files[0]
            file_size = os.path.getsize(video_path)

            # CEK UKURAN VIDEO
            if file_size < MAX_TG_SIZE:
                await msg.edit_text(f"📤 <b>Selesai!</b> Mengirim video ({format_size(file_size)})...", parse_mode="HTML")
                with open(video_path, 'rb') as v:
                    await update.message.reply_video(video=v, caption=f"✅ {os.path.basename(video_path)}")
            else:
                await msg.edit_text(
                    f"🎬 <b>Selesai!</b>\n"
                    f"Ukuran: <b>{format_size(file_size)}</b> (Kegedean buat Telegram).\n"
                    f"Video aman di server Toshiba.", 
                    parse_mode="HTML"
                )
        else:
            await msg.edit_text("❌ Gagal menemukan file video.")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")

# Fungsi alias agar tidak error saat dipanggil
async def dl(u, c): await dls(u, c)
async def yt(u, c): await yts(u, c)