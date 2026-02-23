# 🚀 Zulbot Ultimate - MVC Telegram Bot

[![Server](https://img.shields.io/badge/Server-Toshiba%20Satellite%20C640-green)](https://github.com/5h1n194m1/ubuntu-telegram-bot)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![OS](https://img.shields.io/badge/OS-Ubuntu%2025.10-orange)](https://ubuntu.com/)

Bot Telegram berbasis Python dengan arsitektur **MVC (Model-View-Controller)** yang dirancang khusus untuk berjalan di "Server Bondol" (Toshiba Satellite C640 i5-2450M tanpa casing).

## 💻 Spesifikasi Server (The Bondol Edition)
* **CPU:** Intel® Core™ i5-2450M @ 2.50GHz (2 Cores, 4 Threads)
* **RAM:** 8GB DDR3 1333 MT/s
* **Storage:** HGST HDD 320GB (7200 RPM)
* **OS:** Ubuntu 25.10 (Plucky Puffin)
* **Cooling:** Open Frame Airflow (No Casing)

## 🛠️ Fitur Utama
- **System Monitoring:** Cek suhu CPU, RAM, dan storage secara real-time.
- **MVC Architecture:** Struktur kode rapi dan terpisah.
- **Power Downloader:** Download file ke HP atau Server.
- **Dynamic Info:** Update /info langsung dari Telegram.

## 🎮 Perintah Bot (Commands)
| Command | Deskripsi |
| :--- | :--- |
| /start | Memulai interaksi |
| /status | Cek RAM & Hostname |
| /temp | Monitoring suhu CPU |
| /storage | Cek sisa Hardisk |
| /setinfo | Update info via chat |
| /dls [url] | Download ke Server |

## 📂 Struktur Project
```text
zulbot/
├── app.py              
├── config/             
├── controllers/        
├── models/             
└── utils/              
```

---
*Created by **5h1n194m1** - "Old Hardware, Modern Power"*
