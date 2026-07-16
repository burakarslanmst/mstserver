import os
import sys
import json
import time
import shutil
import hashlib
import socket
import platform
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import psutil
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, send_from_directory, abort

app = Flask(__name__)
app.secret_key = os.urandom(64)

# Konfigürasyon Dosyası ve Varsayılan Ayarlar
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "username": "admin",
    "password_hash": hashlib.sha256("1234".encode("utf-8")).hexdigest(),
    "server_name": "MASTOWLAR ENTERPRISE SERVER",
    "port": 5000,
    "theme": "dark-neon"
}

# Sunucu Log Dosyası
LOG_FILE = "server_activity.log"

def log_event(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level.upper()}] {message}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass

def load_config():
    if not os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            log_event("info", "Varsayılan config.json başarıyla oluşturuldu.")
            return DEFAULT_CONFIG
        except Exception as e:
            log_event("error", f"Config oluşturma hatası: {str(e)}")
            return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_event("error", f"Config yükleme hatası: {str(e)}")
        return DEFAULT_CONFIG

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        log_event("info", "Sistem konfigürasyonu güncellendi.")
        return True
    except Exception as e:
        log_event("error", f"Config kaydetme hatası: {str(e)}")
        return False

# İlk konfigürasyon yüklemesi
SYSTEM_CONFIG = load_config()

def get_drive_list():
    drives = []
    if platform.system() == "Windows":
        import string
        for letter in string.ascii_uppercase:
            drv = f"{letter}:\\"
            if os.path.exists(drv):
                drives.append(drv)
    else:
        drives.append("/")
    return drives

SYSTEM_DRIVES = get_drive_list()
DEFAULT_ROOT_DIR = SYSTEM_DRIVES[0] if SYSTEM_DRIVES else "/"

# Giriş ve Güvenlik Dekoratörleri
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("auth_session"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized access"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Şablonlar (HTML/JS/CSS)
LOGIN_INTERFACE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ server_name }} - Güvenlik Girişi</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0b0f19; }
    </style>
</head>
<body class="text-slate-200 flex items-center justify-center min-h-screen p-4">
    <div class="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-500"></div>
        <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-white tracking-tight">{{ server_name }}</h2>
            <p class="text-xs text-slate-400 mt-2">Kurumsal Yönetim Paneli</p>
        </div>

        {% if error %}
        <div class="bg-red-500/10 border border-red-500/30 text-red-400 text-xs p-3.5 rounded-xl mb-6 flex items-center gap-2">
            ⚠️ {{ error }}
        </div>
        {% endif %}

        <form method="POST" action="/login" class="space-y-5">
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Yönetici Kullanıcı Adı</label>
                <input type="text" name="username" required autocomplete="off" class="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition duration-150" placeholder="Kullanıcı adı">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Giriş Parolası</label>
                <input type="password" name="password" required class="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-white focus:outline-none transition duration-150" placeholder="••••••••">
            </div>
            <button type="submit" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white py-3 rounded-xl text-sm font-semibold transition duration-150 shadow-lg shadow-cyan-600/20">
                Sisteme Bağlan
            </button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_INTERFACE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ server_name }} - Yönetim Konsolu</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #080c14; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #0c1220; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #06b6d4; }
    </style>
</head>
<body class="text-slate-300 min-h-screen pb-12">
    <nav class="bg-slate-900/90 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <div class="flex items-center gap-3">
                    <span class="h-2.5 w-2.5 rounded-full bg-cyan-500 animate-pulse"></span>
                    <span class="font-bold text-white tracking-wide text-sm">{{ server_name }}</span>
                </div>
                <div class="flex items-center gap-4">
                    <span id="system-time" class="text-xs font-mono text-slate-400 hidden md:inline-block">--:--:--</span>
                    <a href="https://mastowlar.com.tr" target="_blank" class="text-xs font-semibold text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 px-3 py-1.5 rounded-lg border border-cyan-500/20">Resmi Websitesi</a>
                    <a href="/logout" class="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 px-3 py-1.5 rounded-lg text-xs font-semibold transition">Çıkış</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-5">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <span class="text-xs font-semibold text-slate-400 block mb-1">CPU KULLANIMI</span>
                <span id="stat-cpu" class="text-2xl font-bold text-white">--%</span>
                <div class="w-full bg-slate-950 h-1 rounded-full mt-3 overflow-hidden">
                    <div id="bar-cpu" class="bg-cyan-500 h-full transition-all duration-500" style="width: 0%"></div>
                </div>
            </div>
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <span class="text-xs font-semibold text-slate-400 block mb-1">RAM KULLANIMI</span>
                <span id="stat-ram" class="text-2xl font-bold text-white">--%</span>
                <div class="w-full bg-slate-950 h-1 rounded-full mt-3 overflow-hidden">
                    <div id="bar-ram" class="bg-purple-500 h-full transition-all duration-500" style="width: 0%"></div>
                </div>
            </div>
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <span class="text-xs font-semibold text-slate-400 block mb-1">C: SÜRÜCÜSÜ</span>
                <span id="stat-disk-c" class="text-2xl font-bold text-white">--%</span>
                <div class="w-full bg-slate-950 h-1 rounded-full mt-3 overflow-hidden">
                    <div id="bar-disk-c" class="bg-emerald-500 h-full transition-all duration-500" style="width: 0%"></div>
                </div>
            </div>
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-5">
                <span class="text-xs font-semibold text-slate-400 block mb-1">D: SÜRÜCÜSÜ</span>
                <span id="stat-disk-d" class="text-2xl font-bold text-white">--%</span>
                <div class="w-full bg-slate-950 h-1 rounded-full mt-3 overflow-hidden">
                    <div id="bar-disk-d" class="bg-indigo-500 h-full transition-all duration-500" style="width: 0%"></div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div class="lg:col-span-8 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                <div class="flex flex-col sm:flex-row items-center justify-between pb-4 border-b border-slate-800 gap-3">
                    <h2 class="text-sm font-bold text-white uppercase tracking-wider">📁 Dosya Sistemi Kontrolü</h2>
                    <div class="flex gap-2 w-full sm:w-auto">
                        <select id="drive-selector" onchange="changeDrive(this.value)" class="bg-slate-950 border border-slate-800 rounded-lg text-xs text-white p-2 outline-none focus:border-cyan-500"></select>
                        <input type="text" id="search-input" onkeyup="filterFiles()" placeholder="Dosyalarda ara..." class="bg-slate-950 border border-slate-800 rounded-lg text-xs text-white p-2 outline-none focus:border-cyan-500 flex-1 sm:w-48">
                    </div>
                </div>

                <div class="flex items-center justify-between text-xs font-mono bg-slate-950/60 p-3 rounded-lg border border-slate-800" id="breadcrumbs"></div>

                <div class="flex flex-wrap gap-2">
                    <button onclick="createNewFolder()" class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition text-slate-200">➕ Yeni Klasör</button>
                    <button onclick="createNewFile()" class="bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold px-3 py-1.5 rounded-lg transition text-slate-200">📄 Yeni Dosya</button>
                    <label class="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition cursor-pointer">
                        ⬆️ Dosya Yükle
                        <input type="file" id="file-uploader" class="hidden" onchange="uploadFile()">
                    </label>
                </div>

                <div class="overflow-x-auto border border-slate-800 rounded-lg">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="bg-slate-950 text-slate-400 text-[11px] font-bold uppercase border-b border-slate-800">
                                <th class="p-3">Adı</th>
                                <th class="p-3">Boyutu</th>
                                <th class="p-3 text-right">Eylemler</th>
                            </tr>
                        </thead>
                        <tbody id="file-table" class="text-xs divide-y divide-slate-800/50 font-mono">
                            <tr><td colspan="3" class="p-6 text-center text-slate-500">Dosyalar aranıyor...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="lg:col-span-4 space-y-6">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4 pb-2 border-b border-slate-800">🔒 Yönetici Kimliği</h3>
                    <div class="space-y-4 text-xs">
                        <div>
                            <label class="block text-slate-400 mb-1">Yeni Kullanıcı Adı</label>
                            <input type="text" id="new-username" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 outline-none focus:border-cyan-500 text-white font-mono" placeholder="Kullanıcı adı">
                        </div>
                        <div>
                            <label class="block text-slate-400 mb-1">Yeni Şifre</label>
                            <input type="password" id="new-password" class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 outline-none focus:border-cyan-500 text-white" placeholder="••••••••">
                        </div>
                        <button onclick="updateCredentials()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white py-2.5 rounded-lg font-semibold transition">Güncelle ve Kaydet</button>
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                    <h3 class="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-slate-800">💻 Sunucu Terminali</h3>
                    <div class="flex gap-2">
                        <input type="text" id="shell-cmd" placeholder="Konsol komutu..." class="flex-1 bg-slate-950 border border-slate-800 rounded-lg text-xs p-2.5 outline-none focus:border-cyan-500 text-cyan-400 font-mono">
                        <button onclick="runCommand()" class="bg-slate-800 hover:bg-slate-700 text-xs px-4 rounded-lg font-bold border border-slate-700 transition">Gönder</button>
                    </div>
                    <pre id="terminal-output" class="bg-slate-950 border border-slate-800 rounded-lg p-3 text-[10px] text-emerald-400 h-40 overflow-y-auto font-mono whitespace-pre-wrap">[MASTOWLAR-SHELL] Bağlantı başarılı. Hazır.</pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentPath = "";
        let originalFiles = [];

        function updateClock() {
            const now = new Date();
            document.getElementById('system-time').innerText = now.toLocaleTimeString('tr-TR');
        }
        setInterval(updateClock, 1000);

        async function fetchSystemStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                
                document.getElementById('stat-cpu').innerText = data.cpu + '%';
                document.getElementById('bar-cpu').style.width = data.cpu + '%';

                document.getElementById('stat-ram').innerText = data.ram + '%';
                document.getElementById('bar-ram').style.width = data.ram + '%';

                document.getElementById('stat-disk-c').innerText = data.disk_c + '%';
                document.getElementById('bar-disk-c').style.width = data.disk_c + '%';

                if(data.disk_d !== null) {
                    document.getElementById('stat-disk-d').innerText = data.disk_d + '%';
                    document.getElementById('bar-disk-d').style.width = data.disk_d + '%';
                } else {
                    document.getElementById('stat-disk-d').innerText = "Yok";
                }

                // Sürücü Listesini Çek
                if (document.getElementById('drive-selector').children.length === 0) {
                    const sel = document.getElementById('drive-selector');
                    data.drives.forEach(d => {
                        const opt = document.createElement('option');
                        opt.value = d;
                        opt.innerText = d;
                        sel.appendChild(opt);
                    });
                    changeDrive(data.drives[0]);
                }
            } catch(e) { console.error("Stats fetching failed", e); }
        }

        function changeDrive(drive) {
            currentPath = drive;
            loadFiles();
        }

        async function loadFiles() {
            try {
                const res = await fetch(`/api/files?path=${encodeURIComponent(currentPath)}`);
                const data = await res.json();
                originalFiles = data;
                renderBreadcrumbs();
                renderFiles(data);
            } catch(e) {
                document.getElementById('file-table').innerHTML = `<tr><td colspan="3" class="p-4 text-center text-red-400">Klasör okuma yetkisi yok.</td></tr>`;
            }
        }

        function renderBreadcrumbs() {
            const container = document.getElementById('breadcrumbs');
            container.innerHTML = `<span onclick="changeDrive('${originalFiles[0]?.root || currentPath}')" class="cursor-pointer text-cyan-400 hover:underline">Kök</span>`;
            
            const parts = currentPath.split(/[\\\\/]/).filter(p => p);
            let built = "";
            parts.forEach((p, i) => {
                built += (i === 0 && p.includes(':')) ? p + "\\\\" : "/" + p;
                container.innerHTML += ` <span class="text-slate-600">/</span> <span onclick="navigateToPath('${built.replace(/\\\\/g, '\\\\\\\\')}')" class="cursor-pointer text-cyan-400 hover:underline">${p}</span>`;
            });
        }

        function navigateToPath(path) {
            currentPath = path;
            loadFiles();
        }

        function renderFiles(files) {
            const body = document.getElementById('file-table');
            body.innerHTML = "";
            if(files.length === 0) {
                body.innerHTML = `<tr><td colspan="3" class="p-6 text-center text-slate-500">Dizin boş.</td></tr>`;
                return;
            }

            files.forEach(f => {
                const typeIcon = f.is_dir ? "📁" : "📄";
                const row = document.createElement('tr');
                row.className = "hover:bg-slate-800/30 transition";

                const nameCol = document.createElement('td');
                nameCol.className = "p-3 flex items-center gap-2";
                if(f.is_dir) {
                    nameCol.innerHTML = `<span>${typeIcon}</span><button onclick="navigateToPath('${f.full_path.replace(/\\\\/g, '\\\\\\\\')}')" class="text-slate-200 hover:text-cyan-400 transition font-semibold text-left truncate max-w-[200px]">${f.name}</button>`;
                } else {
                    nameCol.innerHTML = `<span>${typeIcon}</span><span class="text-slate-300 truncate max-w-[200px]">${f.name}</span>`;
                }

                const sizeCol = document.createElement('td');
                sizeCol.className = "p-3 text-slate-400";
                sizeCol.innerText = f.size;

                const actionCol = document.createElement('td');
                actionCol.className = "p-3 text-right space-x-2";
                if(!f.is_dir) {
                    actionCol.innerHTML += `<a href="/api/download?path=${encodeURIComponent(f.full_path)}" class="text-cyan-400 hover:underline">İndir</a>`;
                }
                actionCol.innerHTML += `<button onclick="deleteItem('${f.full_path.replace(/\\\\/g, '\\\\\\\\')}')" class="text-red-400 hover:underline">Sil</button>`;

                row.appendChild(nameCol);
                row.appendChild(sizeCol);
                row.appendChild(actionCol);
                body.appendChild(row);
            });
        }

        function filterFiles() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const filtered = originalFiles.filter(f => f.name.toLowerCase().includes(query));
            renderFiles(filtered);
        }

        async function createNewFolder() {
            const name = prompt("Yeni Klasör İsmi:");
            if(!name) return;
            const res = await fetch('/api/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: currentPath, name: name, is_dir: true})
            });
            const d = await res.json();
            if(d.success) loadFiles(); else alert("Başarısız: " + d.message);
        }

        async function createNewFile() {
            const name = prompt("Dosya Adı (uzantısıyla):");
            if(!name) return;
            const res = await fetch('/api/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: currentPath, name: name, is_dir: false})
            });
            const d = await res.json();
            if(d.success) loadFiles(); else alert("Başarısız: " + d.message);
        }

        async function deleteItem(path) {
            if(!confirm("Bu öğeyi kalıcı olarak silmek istediğinize emin misiniz?")) return;
            const res = await fetch('/api/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            });
            const d = await res.json();
            if(d.success) loadFiles(); else alert("Başarısız: " + d.message);
        }

        async function uploadFile() {
            const uploader = document.getElementById('file-uploader');
            if(uploader.files.length === 0) return;
            const fd = new FormData();
            fd.append('file', uploader.files[0]);
            fd.append('path', currentPath);

            const res = await fetch('/api/upload', {
                method: 'POST',
                body: fd
            });
            const d = await res.json();
            if(d.success) loadFiles(); else alert("Yükleme başarısız: " + d.message);
        }

        async function runCommand() {
            const inp = document.getElementById('shell-cmd');
            const term = document.getElementById('terminal-output');
            const cmd = inp.value;
            if(!cmd) return;

            term.innerHTML += `\\n$ ${cmd}`;
            term.scrollTop = term.scrollHeight;
            inp.value = "";

            const res = await fetch('/api/shell', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: cmd})
            });
            const d = await res.json();
            term.innerHTML += `\\n${d.output}`;
            term.scrollTop = term.scrollHeight;
        }

        async function updateCredentials() {
            const username = document.getElementById('new-username').value;
            const password = document.getElementById('new-password').value;
            if(!username && !password) {
                alert("Güncellemek istediğiniz bir alanı doldurun.");
                return;
            }

            const res = await fetch('/api/update_creds', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            const d = await res.json();
            if(d.success) {
                alert("Kimlik bilgileri güncellendi! Yeniden giriş yapmalısınız.");
                window.location.href = "/logout";
            } else {
                alert("Hata oluştu.");
            }
        }

        // Başlangıç tetikleyicileri
        fetchSystemStats();
        setInterval(fetchSystemStats, 4000);
    </script>
</body>
</html>
"""

# --- BACKEND API VE YÖNLENDİRME BLOKLARI ---

@app.route("/login", methods=["GET", "POST"])
def login():
    config = load_config()
    if request.method == "POST":
        user = request.form.get("username", "")
        pwd = request.form.get("password", "")
        pwd_hash = hashlib.sha256(pwd.encode("utf-8")).hexdigest()

        if user == config["username"] and pwd_hash == config["password_hash"]:
            session["auth_session"] = True
            log_event("info", f"Başarılı oturum açma: {user}")
            return redirect(url_for("dashboard"))
        
        log_event("warning", f"Hatalı giriş denemesi: {user}")
        return render_template_string(LOGIN_INTERFACE, server_name=config["server_name"], error="Kimlik doğrulama başarısız.")
    
    return render_template_string(LOGIN_INTERFACE, server_name=config["server_name"], error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def dashboard():
    config = load_config()
    return render_template_string(DASHBOARD_INTERFACE, server_name=config["server_name"])

@app.route("/api/stats")
@login_required
def get_stats():
    # Donanım Analizi
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    try:
        disk_c_info = shutil.disk_usage("C:\\" if platform.system() == "Windows" else "/")
        disk_c = round((disk_c_info.used / disk_c_info.total) * 100, 1)
    except Exception:
        disk_c = 0

    disk_d = None
    try:
        if platform.system() == "Windows" and os.path.exists("D:\\"):
            disk_d_info = shutil.disk_usage("D:\\")
            disk_d = round((disk_d_info.used / disk_d_info.total) * 100, 1)
    except Exception:
        pass

    return jsonify({
        "cpu": cpu,
        "ram": ram,
        "disk_c": disk_c,
        "disk_d": disk_d,
        "drives": SYSTEM_DRIVES
    })

@app.route("/api/files")
@login_required
def get_files():
    path_param = request.args.get("path", DEFAULT_ROOT_DIR)
    target_path = Path(path_param).resolve()
    
    if not target_path.exists():
        return jsonify([])

    output_list = []
    try:
        for entry in target_path.iterdir():
            if entry.name.startswith(("$", ".")):
                continue
            
            is_dir = entry.is_dir()
            size = "-"
            if not is_dir:
                try:
                    raw_size = entry.stat().st_size
                    if raw_size < 1024:
                        size = f"{raw_size} B"
                    elif raw_size < 1024**2:
                        size = f"{round(raw_size/1024, 1)} KB"
                    else:
                        size = f"{round(raw_size/(1024**2), 1)} MB"
                except Exception:
                    size = "Korunuyor"

            output_list.append({
                "name": entry.name,
                "is_dir": is_dir,
                "size": size,
                "full_path": str(entry)
            })
    except Exception:
        return jsonify([])

    output_list.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    return jsonify(output_list)

@app.route("/api/create", methods=["POST"])
@login_required
def create_item():
    data = request.json or {}
    parent_path = data.get("path")
    name = data.get("name")
    is_dir = data.get("is_dir", False)

    if not parent_path or not name:
        return jsonify({"success": False, "message": "Geçersiz parametre"})

    try:
        full_path = Path(parent_path) / name
        if is_dir:
            full_path.mkdir(exist_ok=True)
        else:
            full_path.touch()
        log_event("info", f"Yeni öğe oluşturuldu: {str(full_path)}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/delete", methods=["POST"])
@login_required
def delete_item():
    data = request.json or {}
    target = data.get("path")

    if not target or target in SYSTEM_DRIVES:
        return jsonify({"success": False, "message": "Bu dizini silme yetkiniz bulunmuyor."})

    try:
        p = Path(target)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        log_event("info", f"Öğe silindi: {target}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "Dosya seçilmedi."})
    f = request.files["file"]
    dest_path = request.form.get("path")
    if not dest_path:
         return jsonify({"success": False, "message": "Konum geçersiz."})
    try:
        f.save(os.path.join(dest_path, f.filename))
        log_event("info", f"Dosya başarıyla yüklendi: {f.filename} -> {dest_path}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route("/api/download")
@login_required
def download():
    path = request.args.get("path")
    try:
        target = Path(path).resolve()
        return send_from_directory(target.parent, target.name, as_attachment=True)
    except Exception:
        abort(404)

@app.route("/api/shell", methods=["POST"])
@login_required
def run_shell():
    data = request.json or {}
    command = data.get("command", "")
    try:
        out = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="ignore"
        )
        output = out.stdout if out.stdout else out.stderr
        if not output.strip():
            output = "[Sunucu] Komut başarılı bir şekilde icra edildi."
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"output": f"Hata: {str(e)}"})

@app.route("/api/update_creds", methods=["POST"])
@login_required
def update_creds():
    data = request.json or {}
    new_username = data.get("username")
    new_password = data.get("password")

    config = load_config()
    if new_username:
        config["username"] = new_username
    if new_password:
        config["password_hash"] = hashlib.sha256(new_password.encode("utf-8")).hexdigest()
    
    if save_config(config):
        log_event("info", "Yönetici şifresi güncellendi.")
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Kaydetme hatası"})

def print_banner(host, port):
    print("=" * 60)
    print("           💥 MASTOWLAR ENTERPRISE SERVER v2.0 💥")
    print("=" * 60)
    print(f" [+] Başlangıç Tarihi : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    print(f" [+] Yerel Sunucu     : http://127.0.0.1:{port}")
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f" [+] Ağdaki Konumunuz : http://{local_ip}:{port}")
    except Exception:
        pass
    print(" [+] Varsayılan Kullanıcı: admin")
    print(" [+] Varsayılan Şifre   : 1234")
    print("-" * 60)
    print(" [!] Sunucu aktif. Çıkmak için CTRL+C tuş kombinasyonunu kullanın.")
    print("=" * 60)

if __name__ == "__main__":
    app_port = SYSTEM_CONFIG.get("port", 5000)
    print_banner("0.0.0.0", app_port)
    # Debug=False yapılarak kurumsal canlı ortama uyarlandı
    app.run(host="0.0.0.0", port=app_port, debug=False)
