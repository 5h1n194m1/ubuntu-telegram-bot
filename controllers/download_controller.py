
from __future__ import annotations

import asyncio
import shutil
import tempfile
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


async def _run_process(*cmd: str):
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_b, stderr_b = await process.communicate()
    stdout = stdout_b.decode("utf-8", errors="replace").strip()
    stderr = stderr_b.decode("utf-8", errors="replace").strip()
    return process.returncode, stdout, stderr


async def _send_result_file(update: Update, status_msg, file_path: Path):
    size = file_path.stat().st_size
    if size > MAX_TG_SIZE:
        await status_msg.edit_text(
            f"📦 <b>Selesai.</b>\n"
            f"File terlalu besar untuk dikirim ke Telegram: <b>{format_size(size)}</b>.\n"
            f"Gunakan mode server (<code>/dls</code> atau <code>/yts</code>).",
            parse_mode="HTML",
        )
        return

    await status_msg.edit_text(
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


async def _aria2_download(url: str, output_dir: Path, output_name: str):
    ensure_dir(output_dir)
    aria2c = shutil.which("aria2c") or "aria2c"
    cmd = (
        aria2c,
        "--allow-overwrite=true",
        "--continue=true",
        "--max-connection-per-server=8",
        "--split=8",
        "--dir",
        str(output_dir),
        "--out",
        output_name,
        url,
    )
    code, stdout, stderr = await _run_process(*cmd)
    if code != 0:
        raise RuntimeError(stderr or stdout or "aria2c gagal menjalankan download.")
    target = output_dir / output_name
    if not target.exists():
        files = [f for f in output_dir.iterdir() if f.is_file()]
        if not files:
            raise RuntimeError("File hasil download tidak ditemukan.")
        target = max(files, key=lambda p: p.stat().st_mtime)
    return target


async def _ytdlp_download(url: str, output_dir: Path):
    ensure_dir(output_dir)
    yt_dlp = shutil.which("yt-dlp") or "yt-dlp"
    out_template = str(output_dir / "%(title).150s [%(id)s].%(ext)s")
    cmd = (
        yt_dlp,
        "--no-playlist",
        "--newline",
        "--no-progress",
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
    code, stdout, stderr = await _run_process(*cmd)
    if code != 0:
        raise RuntimeError(stderr or stdout or "yt-dlp gagal menjalankan download.")

    printed = [line.strip() for line in stdout.splitlines() if line.strip()]
    if printed:
        candidate = Path(printed[-1]).expanduser()
        if not candidate.is_absolute():
            candidate = (output_dir / candidate).resolve()
        if candidate.exists():
            return candidate

    files = [f for f in output_dir.iterdir() if f.is_file() and not f.name.endswith(".part")]
    if not files:
        raise RuntimeError("File hasil yt-dlp tidak ditemukan.")
    return max(files, key=lambda p: p.stat().st_mtime)


async def _handle_aria2(update: Update, context: ContextTypes.DEFAULT_TYPE, keep_on_server: bool):
    if not is_allowed(update.effective_user.id, ALLOWED_IDS):
        return

    url = get_url_from_update(update, context)
    if not url:
        await update.message.reply_text("❌ Kirim atau reply link dulu, Bos.")
        return

    async def job():
        status_msg = await update.message.reply_text("⏳ <b>Aria2:</b> Men-download...", parse_mode="HTML")
        work_dir = DOWNLOAD_DIR if keep_on_server else Path(tempfile.mkdtemp(prefix="zul_dl_", dir=str(DOWNLOAD_DIR)))
        output_name = _download_label(update, url)

        try:
            file_path = await _aria2_download(url, work_dir, output_name)
            if keep_on_server:
                size = file_path.stat().st_size
                await status_msg.edit_text(
                    f"✅ <b>Selesai.</b>\n"
                    f"Disimpan di server sebagai:\n<code>{file_path.name}</code>\n"
                    f"Ukuran: <b>{format_size(size)}</b>",
                    parse_mode="HTML",
                )
            else:
                await _send_result_file(update, status_msg, file_path)
        except Exception as e:
            await status_msg.edit_text(f"❌ Error: {e}")
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
        status_msg = await update.message.reply_text("🎬 <b>YT-DLP:</b> Sedang memproses video...", parse_mode="HTML")
        work_dir = DOWNLOAD_DIR if keep_on_server else Path(tempfile.mkdtemp(prefix="zul_yt_", dir=str(DOWNLOAD_DIR)))

        try:
            file_path = await _ytdlp_download(url, work_dir)
            if keep_on_server:
                size = file_path.stat().st_size
                await status_msg.edit_text(
                    f"✅ <b>Selesai.</b>\n"
                    f"Disimpan di server sebagai:\n<code>{file_path.name}</code>\n"
                    f"Ukuran: <b>{format_size(size)}</b>",
                    parse_mode="HTML",
                )
            else:
                await _send_result_file(update, status_msg, file_path)
        except Exception as e:
            await status_msg.edit_text(f"❌ Error: {e}")
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
