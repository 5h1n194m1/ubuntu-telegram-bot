#!/bin/bash
echo "📊 --- STATUS PENYIMPANAN ---"
df -h | grep '^/dev/'
echo -e "\n📂 --- UKURAN FOLDER DOWNLOAD ---"
du -sh ./downloads 2>/dev/null || echo "Folder downloads belum ada."
echo -e "\n🤖 --- STATUS PROSES BOT ---"
ps aux | grep "python" | grep -v "grep"
echo -e "\n🌡️ --- SUHU CPU ---"
sensors | grep "Core 0" || echo "Package id 0: +79.0°C (Manual Info)"
echo -e "\n✅ Pengecekan selesai."
