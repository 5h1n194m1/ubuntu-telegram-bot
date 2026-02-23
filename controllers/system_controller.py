# controllers/system_controller.py
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from models.system_model import SystemModel
from utils.helpers import is_allowed
from views.messages import render_start, render_status
import os


#=============================START===============================#
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    try:
        system_data = {
            'os': SystemModel.get_os(),
            'host': SystemModel.get_hostname(),
            'kernel': SystemModel.get_kernel(),
            'uptime': SystemModel.get_uptime(),
            'ip': SystemModel.get_public_ip(),
            'cpu': SystemModel.get_cpu()
        }
        keyboard = [
            ['/start', '/status', '/storage'],
            ['/dl', '/yt', '/dls', '/yts'],
            ['/list', '/info', '/cleanup'],
        ]
        await update.message.reply_text(
            render_start(system_data), 
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error Start: {e}")
# END OF START LOGIC


#=============================STATUS HANDLER===============================#
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    try:
        cpu = SystemModel.get_cpu()
        r = SystemModel.get_ram()
        d = SystemModel.get_disk()
        
        # Pastikan dikirim sebagai LIST agar indices bekerja di view
        ram_data = [r[0], r[1] / (1024**3), r[2] / (1024**3)]
        disk_data = [d[0], d[1] / (1024**3), d[2] / (1024**3)]
        
        msg = render_status(cpu, ram_data, disk_data)
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error Status: {e}")
# END OF STATUS HANDLER

#=============================STORAGE HANDLER===============================#
async def storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    try:
        disk = SystemModel.get_disk()
        msg = (
            f"<pre>"
            f"Total : {disk[2] / (1024**3):.1f} GB\n"
            f"Used  : {disk[1] / (1024**3):.1f} GB\n"
            f"Usage : {disk[0]}%"
            f"</pre>"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error Storage: {e}")
# END OF STORAGE HANDLER


#=============================LIST FILES HANDLER===============================#
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    try:
        files = sorted(DOWNLOAD_DIR.glob("*"), key=os.path.getmtime, reverse=True)
        if not files:
            await update.message.reply_text("Folder kosong.")
            return
        output = "\n".join(f.name for f in files[:20])
        await update.message.reply_text(f"<pre>{output}</pre>", parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error List: {e}")
# END OF LIST FILE HANDLER


#=============================CLEANUP HANDLER===============================#
async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): return

    files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    
    if not files:
        await update.message.reply_text("📂 Folder download sudah kosong, Bos.")
        return

    # List file yang akan dihapus
    file_list = "\n".join([f"• <code>{f}</code>" for f in files])
    text = f"⚠️ <b>KONFIRMASI PENGHAPUSAN</b>\n\nFile berikut akan dihapus permanen:\n{file_list}\n\n<b>Apakah kamu yakin?</b>"

    # Buat tombol konfirmasi
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, Hapus Semua", callback_data="confirm_cleanup"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel_cleanup")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")

# Fungsi untuk memproses pencetan tombol
async def cleanup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_cleanup":
        count = 0
        for file in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        await query.edit_message_text(f"🧹 <b>BERHASIL:</b> {count} file telah dihapus permanen.", parse_mode="HTML")
    
    elif query.data == "cancel_cleanup":
        await query.edit_message_text("❌ <b>DIBATALKAN:</b> File kamu aman, Bos.")
# END OF CLEANUP HANDLER
