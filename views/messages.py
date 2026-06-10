
def render_start(data: dict) -> str:
    temp_val = data.get("temp", "N/A")
    cpu_val = data.get("cpu", 0)

    return f"""
<pre>
███████╗██╗   ██╗██╗
╚══███╔╝██║   ██║██║
  ███╔╝ ██║   ██║██║
 ███╔╝  ██║   ██║██║
███████╗╚██████╔╝███████╗
╚══════╝ ╚═════╝ ╚══════╝

ZULBOT
─────────────────────────
OS     : {data.get('os', 'Ubuntu')}
Host   : {data.get('host', 'ZULBOT')}
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
<code>/temp</code> - Cek suhu CPU
<code>/info</code> - Informasi bot & server

<b>📥 DOWNLOAD KE CHAT</b>
<code>/yt [link]</code> - Download YouTube ke chat
<code>/dl [link]</code> - Download file ke chat

<b>🖥️ DOWNLOAD KE SERVER</b>
<code>/yts [link]</code> - Download YouTube ke server
<code>/dls [link]</code> - Download file ke server

<b>📂 MANAGEMENT</b>
<code>/list</code> - Lihat isi folder & ukuran
<code>/manage</code> - Pilih file untuk dihapus
<code>/cleanup</code> - Hapus semua file

─────────────────────────
<i>Gunakan mode server untuk file besar.</i>
"""

def render_status(cpu, ram, disk, temp) -> str:
    cpu_temp = str(temp).strip() if temp else "N/A"

    return f"""
<b>📊 SYSTEM STATUS</b>
<pre>
CPU  : {cpu:.1f}% ({cpu_temp})
RAM  : {ram[0]}% ({ram[1]:.2f}GB/{ram[2]:.2f}GB)
DISK : {disk[0]}% ({disk[1]:.2f}GB/{disk[2]:.2f}GB)
</pre>
"""
