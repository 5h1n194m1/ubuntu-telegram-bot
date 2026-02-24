# models/system_model.py
import os
import socket
import platform
import psutil
import time
import datetime
import requests

class SystemModel:
    @staticmethod
    def get_hostname():
        return socket.gethostname()

    @staticmethod
    def get_os():
        return f"{platform.system()} {platform.release()}"

    @staticmethod
    def get_kernel():
        return platform.release()

    @staticmethod
    def get_uptime():
        seconds = int(time.time() - psutil.boot_time())
        return str(datetime.timedelta(seconds=seconds))

    @staticmethod
    def get_public_ip():
        try:
            return requests.get("https://api.ipify.org", timeout=3).text
        except:
            return "Unavailable"

    @staticmethod
    def get_cpu():
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_ram():
        ram = psutil.virtual_memory()
        # Return: percent, used, total
        return ram.percent, ram.used, ram.total

    @staticmethod
    def get_disk():
        disk = psutil.disk_usage("/")
        # Return: percent, used, total
        return disk.percent, disk.used, disk.total

    @staticmethod
    def get_cpu_temp():
        # Daftar lokasi sensor suhu umum di Linux
        thermal_paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/thermal/thermal_zone1/temp",
            "/sys/class/hwmon/hwmon0/temp1_input",
            "/sys/class/hwmon/hwmon1/temp1_input"
        ]
        
        for path in thermal_paths:
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        temp = f.read().strip()
                    # Pastikan nilainya angka
                    return f"{int(temp) / 1000:.1f}°C"
            except:
                continue
        
        return "Not Found"