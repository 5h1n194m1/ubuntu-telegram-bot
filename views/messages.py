# views/messages.py

def render_start(data: dict) -> str:
    """
    Menampilkan banner ASCII ZUL dan daftar perintah lengkap.
    Pastikan data berisi: os, host, kernel, uptime, cpu, ip, temp.
    """
    # Ambil suhu dari data, default ke N/A jika tidak ada
    temp_val = data.get('temp', 'N/A')
    cpu_val = data.get('cpu', 0)
    
    return f"""
<pre>
███████╗██╗   ██╗██╗     
╚══███╔╝██║   ██║██║     
  ███╔╝ ██║   ██║██║     
 ███╔╝  ██║   ██║██║     
███████╗╚██████╔╝███████╗
╚══════╝ ╚═════╝ ╚══════╝

ZUL SERVER
─────────────────────────
OS     : {data.get('os', 'Ubuntu')}
Host   : {data.get('host', 'Zul')}
Kernel : {data.get('kernel', 'N/A')}
Uptime : {data.get('uptime', 'N/A')}
CPU    : {cpu_val:.1f}% ({temp_val})
IP     : {data.get('ip', '0.0.0.0')}
</pre>

<b>🎮 DAFTAR PERINTAH (Tap untuk Copy)</b>
─────────────────────────
<b>📊 MONITORING</b>
<code>/status</code> - Detail CPU, RAM & Disk
<code>/storage</code> - Cek sisa kapasitas disk
<code>/info</code> - Informasi bot & server

<b>📥 DOWNLOAD KE DEVICE (Max 50MB)</b>
<code>/yt [link]</code> - Download YouTube ke Chat
<code>/dl [link]</code> - Download File ke Chat

<b>🖥️ DOWNLOAD KE SERVER (Unlimited)</b>
<code>/yts [link]</code> - Download YouTube ke Server
<code>/dls [link]</code> - Download File ke Server

<b>📂 MANAGEMENT</b>
<code>/list</code> - Lihat isi folder download
<code>/cleanup</code> - Hapus semua isi folder
─────────────────────────
<i>Gunakan mode Server untuk file berukuran besar.</i>
"""

def render_status(cpu, ram, disk, temp) -> str:
    """
    Menampilkan status resource sistem.
    ram & disk diharapkan berupa list/tuple: [persen, used, total]
    """
    # Menambahkan pengecekan tipe data temp agar tampilan tetap rapi
    cpu_temp = str(temp).strip() if temp else "N/A"
    
    return f"""
<b>📊 SYSTEM STATUS</b>
<pre>
CPU  : {cpu:.1f}% ({cpu_temp})
RAM  : {ram[0]}% ({ram[1]:.2f}GB/{ram[2]:.2f}GB)
DISK : {disk[0]}% ({disk[1]:.2f}GB/{disk[2]:.2f}GB)
</pre>
"""