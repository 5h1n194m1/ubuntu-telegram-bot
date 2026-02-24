async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    try:
        # 1. Ambil list file di folder download
        files = sorted(DOWNLOAD_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
        
        # 2. Ambil data disk LANGSUNG dari OS agar akurat (Raw Bytes)
        import shutil
        total, used, free = shutil.disk_usage("/") # Mengambil data root /
        
        # Hitung persentase penggunaan
        percent_used = (used / total) * 100
        
        if not files:
            await update.message.reply_text(
                f"📂 <b>Folder kosong, Bos.</b>\n\n"
                f"💾 <b>Sisa Disk:</b> {format_size(free)}", 
                parse_mode="HTML"
            )
            return

        # 3. Rakit daftar file (limit 15 file terbaru)
        file_list = []
        for f in files[:15]:
            size = format_size(f.stat().st_size)
            file_list.append(f"• <code>{f.name}</code>\n  └─ 📦 <b>{size}</b>")
        
        output = (
            f"<b>📂 DAFTAR FILE SERVER</b>\n"
            f"─────────────────────────\n"
            f"{chr(10).join(file_list)}\n"
            f"─────────────────────────\n"
            f"💾 <b>Sisa Disk:</b> {format_size(free)} ({percent_used:.1f}% Used)\n"
            f"<i>Gunakan /cleanup jika sisa disk menipis.</i>"
        )
        
        await update.message.reply_text(output, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error List: {e}")