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
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return f"{int(f.read())/1000:.1f}°C"
        except:
            return "N/A"