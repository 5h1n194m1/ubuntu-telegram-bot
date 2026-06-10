
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from config.settings import DOWNLOAD_DIR, LOG_FILE


class DownloadModel:
    @staticmethod
    def run_download(cmd: list[str]):
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            return subprocess.Popen(
                cmd,
                stdout=log,
                stderr=log,
                cwd=str(DOWNLOAD_DIR),
                text=True,
            )

    @staticmethod
    def aria2_download(link: str, output_dir: str | Path | None = None, output_name: str | None = None):
        output_dir = Path(output_dir or DOWNLOAD_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            shutil.which("aria2c") or "aria2c",
            "--allow-overwrite=true",
            "--continue=true",
            "--max-connection-per-server=8",
            "--split=8",
            "--dir",
            str(output_dir),
        ]
        if output_name:
            cmd += ["--out", output_name]
        cmd.append(link)
        return DownloadModel.run_download(cmd)

    @staticmethod
    def yt_download(link: str, output_dir: str | Path | None = None):
        output_dir = Path(output_dir or DOWNLOAD_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        yt_dlp = shutil.which("yt-dlp") or "yt-dlp"
        cmd = [
            yt_dlp,
            "--no-playlist",
            "--merge-output-format",
            "mp4",
            "-f",
            "bv*+ba/b",
            "-o",
            str(output_dir / "%(title).200s [%(id)s].%(ext)s"),
            link,
        ]
        return DownloadModel.run_download(cmd)

    @staticmethod
    def read_log(lines=30):
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), str(LOG_FILE)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or "Log kosong."
        except Exception:
            return "Gagal membaca log."
