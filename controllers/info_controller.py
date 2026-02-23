# controllers/info_controller.py
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, OWNER_ID
from utils.helpers import is_allowed
from models.info_model import InfoModel

async def setinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. Perbaikan Cek Owner: Gunakan 'not in' karena OWNER_ID adalah Set {...}
    if update.effective_user.id not in OWNER_ID:
        await update.message.reply_text("❌ Akses ditolak. Khusus Owner.")
        return

    # 2. Perbaikan Enter: Ambil teks asli dari pesan, bukan dari context.args
    full_text = update.message.text
    
    # Mencari posisi teks setelah kata /setinfo
    # Kita split maksimal 1 kali berdasarkan spasi pertama
    parts = full_text.split(None, 1)
    
    if len(parts) < 2:
        await update.message.reply_text("❌ Gunakan: <code>/setinfo [teks info]</code>", parse_mode="HTML")
        return

    text = parts[1].strip()
    
    # Simpan ke Model
    InfoModel.set_info(text)
    await update.message.reply_text("✅ <b>Info berhasil diperbarui dengan format baris!</b>", parse_mode="HTML")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    content = InfoModel.get_info()
    if not content or content.strip() == "":
        content = "Belum ada informasi yang diatur."

    try:
        # Kirim dengan mode HTML agar tag <b> atau <code> bekerja
        await update.message.reply_text(content, parse_mode="HTML")
    except Exception:
        # Jika gagal (misal user salah tulis tag HTML), kirim teks polos
        await update.message.reply_text(content)