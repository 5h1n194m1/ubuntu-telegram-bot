# models/info_model.py
import os

INFO_FILE = "data/info_text.txt"

# Pastikan folder data ada
os.makedirs("data", exist_ok=True)

class InfoModel:
    @staticmethod
    def get_info():
        if not os.path.exists(INFO_FILE):
            return "<b>ZUL SERVER INFO</b>\nBelum ada informasi yang diset. Gunakan /setinfo untuk mengisi."
        
        with open(INFO_FILE, "r") as f:
            return f.read()

    @staticmethod
    def set_info(text):
        with open(INFO_FILE, "w") as f:
            f.write(text)