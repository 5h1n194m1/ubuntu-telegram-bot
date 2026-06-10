from __future__ import annotations

import asyncio
import html
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from config.settings import ALLOWED_IDS, DOWNLOAD_DIR, MAX_TG_SIZE, DOWNLOAD_CONCURRENCY
from services.queue_service import QueueService
from utils.helpers import (
    ensure_dir,
    extract_first_url,
    filename_from_url,
    format_size,
    is_allowed,
    sanitize_filename,
    unique_token,
    update_status_message,
)

download_queue = QueueService(max_concurrent=DOWNLOAD_CONCURRENCY)

VALID_VIDEO_SUFFIXES = {".mp4", ".mkv", ".webm", ".mov", ".avi"}


def get_url_from_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    candidates = []

    if message:
        if message.reply_to_message:
            replied = message.reply_to_message.text or message.reply_to_message.caption or ""
            if replied:
                candidates.append(replied)

        if message.text:
            candidates.append(message.text)

        if message.caption:
            candidates.append(message.caption)

    if context.args:
        candidates.append(" ".join(context.args))

    for text in candidates:
        url = extract_first_url(text)
        if url:
            return url

    return None


def _download_label(update: Update, url: str) -> str:
    user = update.effective_user
    short = sanitize_filename(filename_from_url(url, "download"), "download")
    return f"{user.id}_{short}_{unique_token(6)}"


def _which_or_fail(binary_name: str) -> str:
    binary = shutil.which(binary_name)
    if not binary:
        raise RuntimeError(f"{binary_name} tidak ditemukan di server.")
    return binary


async def _run_process_with_progress(cmd: tuple[str, ...], status_msg, title: str, cwd: Path | None = None):
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(cwd) if cwd else None,
    )

    last_update = datetime.now()
    last_line = ""
    lines: list[str] = []

    assert process.stdout is not None
    while True:
        raw = await process.stdout.readline()
        if not raw:
            break

        line = raw.decode("utf-8", errors="replace").replace("\r", "").strip()
        if not line:
            continue

        lines.append(line)
        last_line = line

        now = datetime.now()
        should_update = (now - last_update).total_seconds() >= 1

        if should_update:
            last_update = now
            progress_text = f"⏳ {title}\n{line}"
            await update_status_message(status_msg, progress_text)

    returncode = await process.wait()
    if returncode != 0:
        detail = "\n".join(lines[-20:]) if lines else last_line or "Proses gagal tanpa output."
        raise RuntimeError(detail)

    return lines, last_line


async def _send_result_file(update: Update, status_msg, file_path: Path):
    size = file_path.stat().st_size
    if size > MAX_TG_SIZE:
        await update_status_message(
            status_msg,
            (
                "📦 <b>Selesai.</b>\n"
                f"File terlalu besar untuk dikirim ke Telegram: <b>{format_size(size)}</b>.\n"
                "Gunakan mode server (<code>/dls</code> atau <code>/yts</code>)."
            ),
            parse_mode="HTML",
        )
        return

    await update_status_message(
        status_msg,
        f"📤 <b>Selesai!</b> Mengirim file ({format_size(size)})...",
        parse_mode="HTML",
    )

    with file_path.open("rb") as fh:
        if file_path.suffix.lower() in VALID_VIDEO_SUFFIXES:
            await update.message.reply_video(video=fh, supports_streaming=True)
        else:
            await update.message.reply_document(document=fh)

    try:
        await status_msg.delete()
    except Exception:
        pass


async def _cleanup_path(path: Path):
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink(missing_ok=True)
    except Exception:
        pass


async def _aria2_download(url: str, output_dir: Path, output_name: str, status_msg):
    ensure_dir(output_dir)
    aria2c = _which_or_fail("aria2c")
    cmd = (
        aria2c,
        "--allow-overwrite=true",
        "--continue=true",
        "--max-connection-per-server=8",
        "--split=8",
        "--summary-interval=1",
        "--console-log-level=notice",
        "--dir",
        str(output_dir),
        "--out",
        output_name,
        url,
    )
    lines, _ = await _run_process_with_progress(cmd, status_msg, "Aria2 sedang download...")
    target = output_dir / output_name
    if target.exists():
        return target

    files = [f for f in output_dir.iterdir() if f.is_file()]
    if not files:
        raise RuntimeError("\n".join(lines[-20:]) or "File hasil download tidak ditemukan.")

    return max(files, key=lambda p: p.stat().st_mtime)


async def _ytdlp_download(url: str, output_dir: Path, status_msg):
    ensure_dir(output_dir)
    yt_dlp = _which_or_fail("yt-dlp")
    out_template = str(output_dir / "%(title).150s [%(id)s].%(ext)s")
    cmd = (
        yt_dlp,
        "--no-playlist",
        "--newline",
        "--restrict-filenames",
        "-f",
        "bv*+ba/b",
        "--merge-output-format",
        "mp4",
        "--output",
        out_template,
        "--print",
        "after_move:filepath",
        url,
    )

    lines, _ = await _run_process_with_progress(cmd, status_msg, "YT-DLP sedang download...")
    printed = [line.strip() for line in lines if line.strip()]
    if printed:
        candidate = Path(printed[-1]).expanduser()
        if not candidate.is_absolute():
            candidate = (output_dir / candidate).resolve()
        if candidate.exists():
            return candidate

    files = [f for f in output_dir.iterdir() if f.is_file() and not f.name.endswith(".part")]
    if not files:
        raise RuntimeError("\n".join(lines[-20:]) or "File hasil yt-dlp tidak ditemukan.")

    return max(files, key=lambda p: p.stat().st_mtime)


async def _handle_aria2(update: Update, context: ContextTypes.DEFAULT_TYPE, keep_on_server: bool):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Kirim atau reply link dulu, Bos.")
        return

    async def job():
        status_msg = await update.message.reply_text("⏳ Aria2: menyiapkan download...")
        work_dir = DOWNLOAD_DIR if keep_on_server else Path(tempfile.mkdtemp(prefix="zul_dl_", dir=str(DOWNLOAD_DIR)))
        output_name = _download_label(update, url)

        try:
            file_path = await _aria2_download(url, work_dir, output_name, status_msg)
            if keep_on_server:
                size = file_path.stat().st_size
                await update_status_message(
                    status_msg,
                    (
                        "✅ <b>Selesai.</b>\n"
                        "Disimpan di server sebagai:\n"
                        f"<code>{html.escape(file_path.name)}</code>\n"
                        f"Ukuran: <b>{format_size(size)}</b>"
                    ),
                    parse_mode="HTML",
                )
            else:
                await _send_result_file(update, status_msg, file_path)
        except Exception as e:
            await update_status_message(status_msg, f"❌ Error: {html.escape(str(e))}", parse_mode="HTML")
        finally:
            if not keep_on_server:
                await _cleanup_path(work_dir)

    await download_queue.run(job, user_id=update.effective_user.id)


async def _handle_ytdlp(update: Update, context: ContextTypes.DEFAULT_TYPE, keep_on_server: bool):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Link YouTube-nya mana?")
        return

    async def job():
        status_msg = await update.message.reply_text("🎬 YT-DLP: menyiapkan video...")
        work_dir = DOWNLOAD_DIR if keep_on_server else Path(tempfile.mkdtemp(prefix="zul_yt_", dir=str(DOWNLOAD_DIR)))

        try:
            file_path = await _ytdlp_download(url, work_dir, status_msg)
            if keep_on_server:
                size = file_path.stat().st_size
                await update_status_message(
                    status_msg,
                    (
                        "✅ <b>Selesai.</b>\n"
                        "Disimpan di server sebagai:\n"
                        f"<code>{html.escape(file_path.name)}</code>\n"
                        f"Ukuran: <b>{format_size(size)}</b>"
                    ),
                    parse_mode="HTML",
                )
            else:
                await _send_result_file(update, status_msg, file_path)
        except Exception as e:
            await update_status_message(status_msg, f"❌ Error: {html.escape(str(e))}", parse_mode="HTML")
        finally:
            if not keep_on_server:
                await _cleanup_path(work_dir)

    await download_queue.run(job, user_id=update.effective_user.id)


async def dls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_aria2(update, context, keep_on_server=True)


async def dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_aria2(update, context, keep_on_server=False)


async def yts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_ytdlp(update, context, keep_on_server=True)


async def yt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _handle_ytdlp(update, context, keep_on_server=False)
