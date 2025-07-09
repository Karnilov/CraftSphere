import os
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Перезапуск с правами администратора, если не админ
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
    )
    sys.exit()

import os
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shutil
import sys
import winshell
from win32com.client import Dispatch

GITHUB_TOKEN = "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"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}"
}


GITHUB_FOLDER_URL = "https://github.com/Karnilov/CraftSphere/tree/main/launcher"

def get_api_url(link):
    parts = link.split('/')
    owner, repo = parts[3], parts[4]
    path = '/'.join(parts[7:])
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

def count_files(folder_url):
    try:
        r = requests.get(folder_url, headers=HEADERS)
        r.raise_for_status()
        items = r.json()
    except Exception:
        return 0
    count = 0
    for item in items:
        if item['type'] == 'file':
            count += 1
        elif item['type'] == 'dir':
            count += count_files(item['url'])
    return count

def download_file(file_url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    r = requests.get(file_url)
    with open(save_path, 'wb') as f:
        f.write(r.content)

def download_folder(api_url, local_folder, progress_ui):
    r = requests.get(api_url, headers=HEADERS)
    r.raise_for_status()
    items = r.json()

    for item in items:
        if item['type'] == 'file':
            local_path = os.path.join(local_folder, item['name'])
            download_file(item['download_url'], local_path)
            progress_ui.update(item['name'])
        elif item['type'] == 'dir':
            new_local = os.path.join(local_folder, item['name'])
            download_folder(item['url'], new_local, progress_ui)

class ProgressUI:
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.root = tk.Tk()
        self.root.title("Установка CraftSphere")
        self.root.geometry("400x130")
        self.label = tk.Label(self.root, text="Скачивание файлов...", font=("Arial", 12))
        self.label.pack(pady=10)
        self.progress = ttk.Progressbar(self.root, length=350, maximum=self.total)
        self.progress.pack(pady=5)
        self.percent = tk.Label(self.root, text="0%", font=("Arial", 10))
        self.percent.pack()
        self.root.update()

    def update(self, filename):
        self.current += 1
        self.label.config(text=f"Скачивание: {filename}")
        self.progress["value"] = self.current
        self.percent.config(text=f"{int((self.current / self.total) * 100)}%")
        self.root.update()

    def close(self):
        self.root.destroy()

def create_shortcut(target_path, name="CraftSphere"):
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target_path
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    shortcut.IconLocation = target_path
    shortcut.save()

def show_license_and_get_settings():
    result = {}

    def accept():
        if not license_var.get():
            messagebox.showwarning("Внимание", "Вы должны принять лицензию.")
            return
        result["install_path"] = path_var.get()
        result["shortcut"] = shortcut_var.get()
        win.destroy()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)

    win = tk.Tk()
    win.title("Установщик CraftSphere")
    win.geometry("500x400")

    tk.Label(win, text="Лицензионное соглашение", font=("Arial", 12, "bold")).pack(pady=10)
    license_text = tk.Text(win, height=10, wrap="word")
    license_text.insert("1.0", """\
Лицензионное соглашение

1. Данный лаунчер является частью открытого проекта CraftSphere, разработанного сообществом InterplanetaryHackers.
2. Вы можете свободно использовать, копировать, распространять и модифицировать данный лаунчер без ограничений.
3. Разработчики предоставляют программу "как есть" — без каких-либо гарантий работоспособности или соответствия конкретным задачам.
4. Авторы не несут ответственности за возможные ошибки, повреждение данных или иной ущерб, вызванный использованием данного программного обеспечения.
5. Использование лаунчера означает согласие с условиями этого соглашения и признание его открытого статуса.
    """)

    license_text.config(state="disabled")
    license_text.pack(padx=10, pady=5)

    license_var = tk.BooleanVar()
    shortcut_var = tk.BooleanVar()
    path_var = tk.StringVar(value=os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "CraftSphere"))

    tk.Checkbutton(win, text="Я принимаю условия лицензионного соглашения", variable=license_var).pack(pady=5)
    tk.Label(win, text="Путь установки:").pack()
    path_frame = tk.Frame(win)
    path_entry = tk.Entry(path_frame, textvariable=path_var, width=50)
    path_entry.pack(side="left", padx=5)
    tk.Button(path_frame, text="Обзор", command=browse_folder).pack(side="left")
    path_frame.pack(pady=5)

    tk.Checkbutton(win, text="Создать ярлык на рабочем столе", variable=shortcut_var).pack(pady=10)
    tk.Button(win, text="Установить", command=accept, bg="#28a745", fg="white", width=20).pack(pady=10)

    win.mainloop()
    return result

def run_installer():
    settings = show_license_and_get_settings()
    if not settings:
        return

    install_path = settings["install_path"]
    create_shortcut_flag = settings["shortcut"]

    api_url = get_api_url(GITHUB_FOLDER_URL)
    total_files = count_files(api_url)

    if os.path.exists(install_path):
        try:
            shutil.rmtree(install_path)
        except Exception as e:
            print(f"Ошибка очистки папки: {e}")

    os.makedirs(install_path, exist_ok=True)

    ui = ProgressUI(total_files)
    download_folder(api_url, install_path, ui)
    ui.close()

    if create_shortcut_flag:
        exe_or_launcher = os.path.join(install_path, "main.exe" if os.path.exists(os.path.join(install_path, "main.exe")) else "main.py")
        create_shortcut(exe_or_launcher)

    tk.messagebox.showinfo("Готово", f"Установка завершена в:\n{install_path}")

if __name__ == "__main__":
    run_installer()
