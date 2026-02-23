# controllers/download_controller.py
import os
import requests
import subprocess
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from utils.helpers import is_allowed

# --- DOWNLOAD KE SERVER (dls & yts) ---

async def dls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    if not context.args:
        await update.message.reply_text("❌ Gunakan: <code>/dls [link]</code>", parse_mode="HTML")
        return

    url = context.args[0]
    filename = url.split("/")[-1].split("?")[0] or "file_server"
    save_path = os.path.join(DOWNLOAD_DIR, filename)
    
    msg = await update.message.reply_text(f"⏳ <b>SERVER:</b> Mendownload...\n📄 <code>{filename}</code>", parse_mode="HTML")

    try:
        with requests.get(url, stream=True, timeout=20) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024): # 1MB Chunk
                    f.write(chunk)
        await msg.edit_text(f"✅ <b>Selesai ke Server!</b>\n📂 Lokasi: <code>{save_path}</code>", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"❌ <b>Gagal:</b> {str(e)}")

async def yts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    if not context.args:
        await update.message.reply_text("❌ Gunakan: <code>/yts [link_yt]</code>", parse_mode="HTML")
        return

    link = context.args[0]
    await update.message.reply_text("🎬 <b>YT-DLP:</b> Memproses ke storage server...")
    
    # Jalankan yt-dlp secara background menggunakan subprocess
    try:
        subprocess.Popen(["yt-dlp", "-P", str(DOWNLOAD_DIR), "-f", "mp4", link])
    except Exception as e:
        await update.message.reply_text(f"❌ Error menjalankan yt-dlp: {e}")

# --- DOWNLOAD KE DEVICE (dl & yt) ---

async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    if not context.args:
        await update.message.reply_text("❌ Gunakan: <code>/dl [link]</code>")
        return

    url = context.args[0]
    msg = await update.message.reply_text("📥 Mengambil file untuk HP...")
    
    try:
        response = requests.get(url, timeout=15)
        # Limit 50MB karena batasan bot Telegram
        if len(response.content) > 50 * 1024 * 1024:
            await msg.edit_text("⚠️ File > 50MB. Gunakan <code>/dls</code> untuk simpan di server.")
            return
        
        filename = url.split("/")[-1].split("?")[0] or "file_hp"
        await update.message.reply_document(document=response.content, filename=filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Gagal: {e}")

async def yt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    await update.message.reply_text("🛠 Fitur YT ke Device sedang dikembangkan. Gunakan <code>/yts</code> sementara.")