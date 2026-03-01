#!/bin/bash
# Simpan sebagai: sync.sh

echo "📤 Memulai proses Git Push..."
git add .
read -p "Masukkan pesan commit: " commit_msg
git commit -m "$commit_msg"
git push origin main # Ganti 'main' jika branch kamu beda
echo "✅ Kode berhasil di-push ke Git."

echo "🔄 Merestart service agar perubahan diterapkan..."
sudo systemctl restart zul.service
echo "🚀 Selesai!"