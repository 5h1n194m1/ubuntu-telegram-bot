# controllers/system_controller.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from models.system_model import SystemModel
from views.messages import render_start, render_status
from utils.helpers import is_allowed

# ============================= START HANDLER =============================== #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    try:
        # Mengambil data sistem untuk dikirim ke view
        system_data = {
            'os': SystemModel.get_os(),
            'host': SystemModel.get_hostname(),
            'kernel': SystemModel.get_kernel(),
            'uptime': SystemModel.get_uptime(),
            'ip': SystemModel.get_public_ip(),
            'cpu': SystemModel.get_cpu()
        }

        # Menu tombol cepat di bawah (Keyboard Menu)
        keyboard = [
            ['/start', '/status', '/storage'],
            ['/dl', '/yt', '/dls', '/yts'],
            ['/list', '/info', '/cleanup'],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            render_start(system_data), 
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error Start: {e}")

# ============================= STATUS HANDLER =============================== #
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    try:
        cpu = SystemModel.get_cpu()
        temp = SystemModel.get_cpu_temp()
        r = SystemModel.get_ram()   # [persen, used, total]
        d = SystemModel.get_disk()  # [persen, used, total]
        
        # Konversi ke GB agar tampilan rapi di render_status
        ram_data = [r[0], r[1] / (1024**3), r[2] / (1024**3)]
        disk_data = [d[0], d[1] / (1024**3), d[2] / (1024**3)]
        
        msg = render_status(cpu, ram_data, disk_data, temp)
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error Status: {e}")

# ============================= STORAGE HANDLER =============================== #
async def storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    try:
        disk = SystemModel.get_disk()
        msg = (
            f"<b>💾 Disk Usage Info</b>\n"
            f"<pre>"
            f"Total : {disk[2] / (1024**3):.1f} GB\n"
            f"Used  : {disk[1] / (1024**3):.1f} GB\n"
            f"Free  : {(disk[2]-disk[1]) / (1024**3):.1f} GB\n"
            f"Usage : {disk[0]}%"
            f"</pre>"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error Storage: {e}")

# ============================= LIST FILES HANDLER =============================== #
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    try:
        # Mengambil daftar file di folder downloads
        files = sorted(DOWNLOAD_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
        
        if not files:
            await update.message.reply_text("📂 <b>Folder kosong, Bos.</b>", parse_mode="HTML")
            return

        # Ambil 20 file terbaru
        file_list = "\n".join([f"• <code>{f.name}</code>" for f in files[:20]])
        output = f"<b>📂 Daftar File (20 Terbaru):</b>\n\n{file_list}"
        
        await update.message.reply_text(output, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error List: {e}")

# ============================= CLEANUP HANDLER =============================== #
async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS): 
        return

    # Cek apakah ada file sebelum konfirmasi hapus
    files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    
    if not files:
        await update.message.reply_text("🧹 <b>Folder download sudah bersih, Bos.</b>", parse_mode="HTML")
        return

    # Siapkan pesan konfirmasi
    file_list = "\n".join([f"• <code>{f}</code>" for f in files[:10]])
    if len(files) > 10: file_list += f"\n...dan {len(files)-10} file lainnya."

    text = (
        f"⚠️ <b>KONFIRMASI PENGHAPUSAN</b>\n\n"
        f"File berikut akan dihapus dari server Toshiba:\n{file_list}\n\n"
        f"<b>Apakah kamu yakin?</b>"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, Hapus Semua", callback_data="confirm_cleanup"),
            InlineKeyboardButton("❌ Batal", callback_data="cancel_cleanup")
        ]
    ]
    
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="HTML"
    )

async def cleanup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memproses klik tombol pada menu cleanup."""
    query = update.callback_query
    if not is_allowed(query.from_user.id, ALLOWED_IDS):
        await query.answer("Akses Ditolak!", show_alert=True)
        return

    await query.answer()

    if query.data == "confirm_cleanup":
        count = 0
        for file in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            except: pass
        await query.edit_message_text(f"🧹 <b>BERHASIL:</b> {count} file telah dihapus permanen dari server.", parse_mode="HTML")
    
    elif query.data == "cancel_cleanup":
        await query.edit_message_text("❌ <b>DIBATALKAN:</b> File aman di storage server.", parse_mode="HTML")