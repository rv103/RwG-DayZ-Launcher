# RwG_Launcher.py

import os
import json
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime, timezone
import webbrowser
import requests
import urllib.request
import zipfile
import shutil
import sys
import tempfile

# ========== KONFIGURATION ==========
CONFIG_FILE = "config.json"
CURRENT_VERSION = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/rv103/RwG-DayZ-Launcher/main/version.txt"
ZIP_URL = "https://github.com/rv103/RwG-DayZ-Launcher/releases/latest/download/RwG_Launcher.zip"
SERVER_IP = "95.156.230.51"
SERVER_PORT = "2302"
SERVER_PASSWORD = "111"
MOD_TITLES = {
    "1559212036": "CF",
    "2545327648": "Dabs Framework",
    "1564026768": "Community-Online-Tools",
    "1828439124": "VPPAdminTools",
    "2464526692": "GameLabs",
    "2116157322": "DayZ-Expansion-Licensed",
    "2572331007": "DayZ-Expansion-Bundle",
    "2793893086": "DayZ-Expansion-Animations",
    "3442514175": "RwG Addon DZ Server",
    "3381664818": "Ninjins-PvP-PvE"
}
MOD_IDS = list(MOD_TITLES.keys())
# ====================================


def fetch_steam_mod_timestamps(mod_ids):
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    data = {
        "itemcount": len(mod_ids),
        **{f"publishedfileids[{i}]": mod_id for i, mod_id in enumerate(mod_ids)}
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    results = response.json()["response"]["publishedfiledetails"]
    return {
        item["publishedfileid"]: datetime.fromtimestamp(item["time_updated"], tz=timezone.utc)
        for item in results
    }


def check_for_updates():
    try:
        with urllib.request.urlopen(VERSION_URL) as response:
            latest_version = response.read().decode().strip()
        if latest_version != CURRENT_VERSION:
            answer = messagebox.askyesno("Update verfügbar", f"Version {latest_version} ist verfügbar.\nJetzt aktualisieren?")
            if answer:
                download_and_update()
    except Exception as e:
        print(f"[Updater] Fehler beim Update-Check: {e}")


def download_and_update():
    try:
        tmp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(tmp_dir, "update.zip")
        with urllib.request.urlopen(ZIP_URL) as response, open(zip_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if os.path.basename(member) == "config.json":
                    continue
                zip_ref.extract(member, tmp_dir)

        for root_dir, _, files in os.walk(tmp_dir):
            for file in files:
                if file == "config.json":
                    continue
                src_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(src_path, tmp_dir)
                dst_path = os.path.join(os.getcwd(), rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.move(src_path, dst_path)

        messagebox.showinfo("Update abgeschlossen", "Die neue Version wurde installiert. Der Launcher wird neu gestartet.")
        restart_launcher()

    except Exception as e:
        messagebox.showerror("Update-Fehler", f"Fehler beim Update:\n{e}")


def restart_launcher():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def write_version_file():
    try:
        with open("version.txt", "w") as f:
            f.write(CURRENT_VERSION)
    except Exception as e:
        print(f"[Version] Fehler beim Schreiben von version.txt: {e}")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)


def resolve_paths():
    config = load_config()

    if not config.get("dayz_path") or not os.path.exists(config["dayz_path"]):
        path = filedialog.askdirectory(title="DayZ-Installationsverzeichnis auswählen")
        config["dayz_path"] = path

    if not config.get("workshop_path") or not os.path.exists(config["workshop_path"]):
        path = filedialog.askdirectory(title="Steam Workshop-Verzeichnis (221100) auswählen")
        config["workshop_path"] = path

    save_config(config)
    return config["dayz_path"], config["workshop_path"]


def resolve_mods(workshop_path):
    local_mods = []
    for mod_id in MOD_IDS:
        path = os.path.join(workshop_path, mod_id)
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            local_mods.append((mod_id, path, datetime.fromtimestamp(mtime, tz=timezone.utc)))
        else:
            local_mods.append((mod_id, None, None))
    return local_mods


def start_dayz(use_battleye, with_splash, nopause, mod_string, dayz_path):
    exe = os.path.join(dayz_path, "DayZ_BE.exe" if use_battleye else "DayZ_x64.exe")
    if not os.path.exists(exe):
        messagebox.showerror("Fehler", f"{exe} nicht gefunden!")
        return

    command = [
        exe,
        f"-connect={SERVER_IP}",
        f"-port={SERVER_PORT}",
        f"-password={SERVER_PASSWORD}",
        f"-mod={mod_string}"
    ]
    if not with_splash:
        command.append("-nosplash")
    if nopause in ("0", "1"):
        command.append(f"-noPause={nopause}")

    subprocess.Popen(command)


def run_gui():
    check_for_updates()

    def refresh():
        root.destroy()
        run_gui()

    dayz_path, workshop_path = resolve_paths()
    local_mods = resolve_mods(workshop_path)
    steam_mods = fetch_steam_mod_timestamps(MOD_IDS)

    mod_string = ";".join([os.path.join(workshop_path, mod[0]) for mod in local_mods if mod[1]])

    global root
    root = tk.Tk()
    root.title("RwG DayZ Launcher")
    root.geometry("700x720")
    root.configure(bg="#1e1e1e")

    tk.Label(root, text="RwG DayZ Launcher", font=("Segoe UI", 18, "bold"), bg="#1e1e1e", fg="white").pack(pady=12)
    tk.Label(root, text=f"DayZ Pfad: {dayz_path}", fg="gray", bg="#1e1e1e").pack()
    tk.Label(root, text=f"Workshop Pfad: {workshop_path}", fg="gray", bg="#1e1e1e").pack()

    # Main content frame
    content_frame = tk.Frame(root, bg="#1e1e1e")
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    mod_frame = tk.Frame(content_frame, bg="#2b2b2b")
    mod_frame.pack(pady=5, fill="both", expand=True)
    tk.Label(mod_frame, text="Modstatus", font=("Segoe UI", 13, "bold"), bg="#2b2b2b", fg="white").pack(anchor="w", pady=5)

    for mod_id, path, local_time in local_mods:
        frame = tk.Frame(mod_frame, bg="#2b2b2b")
        frame.pack(anchor="w", fill="x", pady=1, padx=5)
        title = MOD_TITLES.get(mod_id, mod_id)
        label = tk.Label(frame, text=title, width=40, anchor="w", bg="#2b2b2b", fg="white", cursor="hand2")
        label.pack(side="left", padx=5)
        label.bind("<Button-1>", lambda e, mid=mod_id: webbrowser.open(f"steam://openurl/https://steamcommunity.com/sharedfiles/filedetails/?id={mid}"))

        canvas = tk.Canvas(frame, width=20, height=20, highlightthickness=0, bg="#2b2b2b")
        canvas.pack(side="left")

        if not path:
            color = "red"
            tooltip = "Mod nicht installiert"
        else:
            steam_time = steam_mods.get(mod_id)
            if steam_time and local_time < steam_time:
                color = "yellow"
                tooltip = f"Lokal: {local_time.strftime('%Y-%m-%d %H:%M:%S')}\nSteam: {steam_time.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                color = "green"
                tooltip = f"Lokal: {local_time.strftime('%Y-%m-%d %H:%M:%S')}\nSteam: {steam_time.strftime('%Y-%m-%d %H:%M:%S')}"

        canvas.create_oval(5, 5, 15, 15, fill=color)

        def on_enter(event, text=tooltip):
            tooltip_win = tk.Toplevel()
            tooltip_win.wm_overrideredirect(True)
            tooltip_win.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 5}")
            label = tk.Label(tooltip_win, text=text, background="#333", foreground="white", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            label.pack()
            event.widget.tooltip = tooltip_win

        def on_leave(event):
            if hasattr(event.widget, "tooltip"):
                event.widget.tooltip.destroy()
                event.widget.tooltip = None

        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

    # Bottom frame (footer)
    footer_frame = tk.Frame(root, bg="#1e1e1e")
    footer_frame.pack(side="bottom", fill="x", padx=20, pady=10)

    # Left settings
    left_frame = tk.Frame(footer_frame, bg="#1e1e1e")
    left_frame.pack(side="left", anchor="sw")

    splash_var = tk.BooleanVar(value=False)
    tk.Checkbutton(left_frame, text="Mit Ladebildschirm starten", variable=splash_var, bg="#1e1e1e", fg="white", selectcolor="#1e1e1e").pack(anchor="w", pady=3)

    tk.Label(left_frame, text="Pause-Verhalten (noPause):", bg="#1e1e1e", fg="white").pack(anchor="w")
    pause_desc = {
        "deaktiviert": "→ Spiel pausiert im Menü",
        "0": "→ Grafik pausiert, Sound läuft",
        "1": "→ Spiel läuft im Menü weiter"
    }
    pause_var = tk.StringVar(value="1")
    pause_menu = ttk.Combobox(left_frame, textvariable=pause_var, values=list(pause_desc.keys()), state="readonly")
    pause_menu.pack(anchor="w")
    pause_label = tk.Label(left_frame, text=pause_desc[pause_var.get()], bg="#1e1e1e", fg="gray")
    pause_label.pack(anchor="w")

    def update_desc(*args):
        pause_label.config(text=pause_desc[pause_var.get()])
    pause_var.trace_add("write", update_desc)

    # Right buttons
    right_frame = tk.Frame(footer_frame, bg="#1e1e1e")
    right_frame.pack(side="right", anchor="se")

    tk.Button(right_frame, text="Mit Battleye starten", bg="#4CAF50", fg="white",
              font=("Segoe UI", 11, "bold"), width=25,
              command=lambda: start_dayz(True, splash_var.get(),
                                         pause_var.get() if pause_var.get() in ["0", "1"] else "",
                                         mod_string, dayz_path)).pack(pady=5)

    tk.Button(right_frame, text="Ohne Battleye starten", bg="#f39c12", fg="white",
              font=("Segoe UI", 11, "bold"), width=25,
              command=lambda: start_dayz(False, splash_var.get(),
                                         pause_var.get() if pause_var.get() in ["0", "1"] else "",
                                         mod_string, dayz_path)).pack()

    root.mainloop()


if __name__ == "__main__":
    write_version_file()
    run_gui()
