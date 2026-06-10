
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import ALLOWED_IDS, OWNER_ID
from models.info_model import InfoModel
from utils.helpers import is_allowed


async def setinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Akses ditolak. Khusus Owner.")
        return

    full_text = update.message.text or ""
    parts = full_text.split(None, 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("❌ Gunakan: <code>/setinfo [teks info]</code>", parse_mode="HTML")
        return

    text = parts[1].rstrip()
    InfoModel.set_info(text)
    await update.message.reply_text("✅ <b>Info berhasil diperbarui.</b>", parse_mode="HTML")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    content = InfoModel.get_info()
    try:
        await update.message.reply_text(content, parse_mode="HTML")
    except Exception:
        await update.message.reply_text(content)
