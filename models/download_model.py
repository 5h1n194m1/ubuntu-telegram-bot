# models/download_model.py
# Logic download & log

import subprocess
from config.settings import DOWNLOAD_DIR, LOG_FILE

class DownloadModel:

    @staticmethod
    def run_download(cmd: list):
        # Jalankan download dan log ke file
        with open(LOG_FILE, "a") as log:
            subprocess.Popen(cmd, stdout=log, stderr=log)

    @staticmethod
    def aria2_download(link: str):
        cmd = [
            "aria2c",
            "-d", str(DOWNLOAD_DIR),
            "-x", "16",
            "-s", "16",
            link
        ]
        DownloadModel.run_download(cmd)

    @staticmethod
    def yt_download(link: str):
        cmd = [
            "/usr/local/bin/yt-dlp",
            "-P", str(DOWNLOAD_DIR),
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            link
        ]
        DownloadModel.run_download(cmd)

    @staticmethod
    def read_log(lines=30):
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), str(LOG_FILE)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or "Log kosong."
        except:
            return "Gagal membaca log."
