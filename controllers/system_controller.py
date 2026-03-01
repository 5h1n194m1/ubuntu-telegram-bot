# controllers/system_controller.py
import os
import shutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import ALLOWED_IDS, DOWNLOAD_DIR
from models.system_model import SystemModel
from views.messages import render_start, render_status
from utils.helpers import is_allowed, format_size

# ============================= START HANDLER =============================== #
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
            'cpu': SystemModel.get_cpu(),
            'temp': SystemModel.get_cpu_temp()
        }
        keyboard = [
            ['/start', '/status', '/storage'],
            ['/list', '/manage', '/cleanup'],
            ['/dl', '/yt', '/dls', '/yts'],
            ['/info']
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
        r = SystemModel.get_ram()
        d = SystemModel.get_disk()
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
        files = sorted(DOWNLOAD_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
        total, used, free = shutil.disk_usage("/")
        percent_used = (used / total) * 100

        if not files:
            await update.message.reply_text(f"📂 <b>Folder kosong, Bos.</b>\n💾 <b>Sisa Disk:</b> {format_size(free)}", parse_mode="HTML")
            return

        file_list = [f"• <code>{f.name}</code>\n  └─ 📦 <b>{format_size(f.stat().st_size)}</b>" for f in files[:15]]
        output = (
            f"<b>📂 DAFTAR FILE SERVER</b>\n─────────────────────────\n"
            f"{chr(10).join(file_list)}\n─────────────────────────\n"
            f"💾 <b>Sisa Disk:</b> {format_size(free)} ({percent_used:.1f}% Used)\n"
            f"<i>Gunakan /cleanup jika sisa disk menipis.</i>"
        )
        await update.message.reply_text(output, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error List: {e}")

# ============================= MANAGE FILES =============================== #
async def manage_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    try:
        files = sorted(list(DOWNLOAD_DIR.glob("*")), key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            await update.message.reply_text("📂 <b>Folder kosong.</b>", parse_mode="HTML")
            return
        keyboard = []
        text = "<b>🛠️ PENGELOLAAN FILE</b>\n─────────────────────────\n"
        for i, f in enumerate(files[:10]):
            text += f"{i+1}. <code>{f.name}</code> (<b>{format_size(f.stat().st_size)}</b>)\n"
            keyboard.append([InlineKeyboardButton(f"🗑️ Hapus File {i+1}", callback_data=f"askdel_{i}")])
        keyboard.append([InlineKeyboardButton("❌ Tutup Menu", callback_data="cancel_cleanup")])
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error Manage: {e}")

# ============================= CLEANUP TRIGGER =============================== #
async def cleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return
    files = [f for f in os.listdir(DOWNLOAD_DIR) if os.path.isfile(os.path.join(DOWNLOAD_DIR, f))]
    if not files:
        await update.message.reply_text("🧹 <b>Folder sudah bersih.</b>", parse_mode="HTML")
        return
    text = f"⚠️ <b>KONFIRMASI PENGHAPUSAN MASSAL</b>\n\nApakah kamu yakin ingin menghapus <b>{len(files)}</b> file?"
    keyboard = [[InlineKeyboardButton("✅ Ya, Hapus Semua", callback_data="confirm_cleanup"),
                 InlineKeyboardButton("❌ Batal", callback_data="cancel_cleanup")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

# ============================= CALLBACK HANDLER =============================== #
async def cleanup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if not is_allowed(query.from_user.id, ALLOWED_IDS):
        await query.answer("Akses Ditolak!", show_alert=True)
        return
    await query.answer()
    try:
        files = sorted(list(DOWNLOAD_DIR.glob("*")), key=lambda f: f.stat().st_mtime, reverse=True)
        # 1. Logic REDIRECT YTS (Download via Server)
        if data.startswith("yts_redir_"):
            link = data.replace("yts_redir_", "")
            await query.edit_message_text("🚀 <b>Ok Bos!</b> Mengalihkan download ke server (Full HD)...", parse_mode="HTML")
            
            process = await asyncio.create_subprocess_exec(
                "yt-dlp", "-P", str(DOWNLOAD_DIR), 
                "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]", 
                "--merge-output-format", "mp4", link
            )
            await process.wait()
            await query.message.reply_text(f"✅ <b>Selesai!</b> Video sudah ada di server.\nCek via /list.")

        # 2. Logic KONFIRMASI HAPUS SATUAN
        elif data.startswith("askdel_"):
            idx = int(data.split("_")[1])
            if idx < len(files):
                target = files[idx]
                text = f"⚠️ <b>HAPUS SATUAN?</b>\n\n<code>{target.name}</code>"
                kb = [[InlineKeyboardButton("✅ Ya", callback_data=f"confdel_{idx}"), InlineKeyboardButton("❌ Batal", callback_data="cancel_cleanup")]]
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        
        # 3. Logic EKSEKUSI HAPUS SATUAN
        elif data.startswith("confdel_"):
            idx = int(data.split("_")[1])
            if idx < len(files):
                filename = files[idx].name
                os.remove(files[idx])
                await query.edit_message_text(f"✅ <b>{filename}</b> berhasil dihapus.", parse_mode="HTML")
        
        # 4. Logic HAPUS SEMUA
        elif data == "confirm_cleanup":
            count = 0
            for f in os.listdir(DOWNLOAD_DIR):
                file_path = os.path.join(DOWNLOAD_DIR, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    count += 1
            await query.edit_message_text(f"🧹 Folder dikosongkan ({count} file dihapus).")
        
        # 5. Logic BATAL
        elif data == "cancel_cleanup":
            await query.edit_message_text("❌ Aksi dibatalkan.")

    except Exception as e:
        await query.edit_message_text(f"❌ <b>Error Callback:</b> {str(e)}", parse_mode="HTML")