#!/bin/bash
# Simpan sebagai: manage.sh

SERVICE_NAME="zul.service"

case "$1" in
    start)
        sudo systemctl start $SERVICE_NAME
        echo "✅ Bot dinyalakan."
        ;;
    stop)
        sudo systemctl stop $SERVICE_NAME
        echo "🛑 Bot dimatikan."
        ;;
    restart)
        sudo systemctl restart $SERVICE_NAME
        echo "🔄 Bot direstart."
        ;;
    status)
        sudo systemctl status $SERVICE_NAME
        ;;
    log)
        echo "👀 Menampilkan log (Tekan Ctrl+C untuk keluar):"
        journalctl -u $SERVICE_NAME -f
        ;;
    *)
        echo "Cara pakai: ./manage.sh {start|stop|restart|status|log}"
        ;;
esac