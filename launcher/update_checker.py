import os
import shutil
import requests
import tkinter as tk
from tkinter import messagebox, ttk
import sys

# === Константы ===
GITHUB_FOLDER_LINK = "https://github.com/Karnilov/CraftSphere/tree/main/launcher"
GITHUB_RAW_VERSION = "https://raw.githubusercontent.com/Karnilov/CraftSphere/main/launcher/version.txt"
LOCAL_VERSION_FILE = "version.txt"
EXCLUDE_FILES = {os.path.basename(__file__), "update_checker.py"}  # Не удалять этот файл
DOWNLOAD_FOLDER = "."  # Сюда сохраняются файлы

# === GitHub API ===
def getUrl(link):
    lk = link.split('/')
    owner, repo = lk[3], lk[4]
    path = '/'.join(lk[7:])
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

def count_files(folder_url):
    try:
        r = requests.get(folder_url)
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

# === Скачивание с прогрессом ===
class ProgressDownloader:
    def __init__(self, total_files):
        self.total = total_files
        self.current = 0
        self.root = tk.Tk()
        self.root.title("Обновление")
        self.root.geometry("400x120")
        self.label = tk.Label(self.root, text="Подготовка...", font=("Arial", 12))
        self.label.pack(pady=10)
        self.progress = ttk.Progressbar(self.root, length=350, maximum=self.total, mode='determinate')
        self.progress.pack(pady=5)
        self.percent = tk.Label(self.root, text="0%", font=("Arial", 10))
        self.percent.pack()
        self.root.update()

    def update(self, filename):
        self.current += 1
        self.label.config(text=f"Загрузка: {filename}")
        self.progress["value"] = self.current
        percent_value = int((self.current / self.total) * 100)
        self.percent.config(text=f"{percent_value}%")
        self.root.update()

    def close(self):
        self.root.destroy()

def download_file(file_url, folder_path):
    response = requests.get(file_url)
    filename = os.path.join(folder_path, os.path.basename(file_url))
    os.makedirs(folder_path, exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(response.content)

def download_folder_contents(folder_url, folder_path, progress_ui=None):
    try:
        r = requests.get(folder_url)
        r.raise_for_status()
        items = r.json()
    except Exception as e:
        print(f"❌ Ошибка при получении содержимого папки: {e}")
        return

    for item in items:
        if item['type'] == 'file':
            download_file(item['download_url'], folder_path)
            if progress_ui:
                progress_ui.update(item['name'])
        elif item['type'] == 'dir':
            new_folder = os.path.join(folder_path, item['name'])
            download_folder_contents(item['url'], new_folder, progress_ui)

# === Версия ===
def get_local_version():
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_remote_version():
    try:
        response = requests.get(GITHUB_RAW_VERSION)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"❌ Не удалось получить удалённую версию: {e}")
        return None

def compare_versions(local, remote):
    return tuple(map(int, remote.split("."))) > tuple(map(int, local.split(".")))

# === Очистка ===
def delete_old_files():
    for f in os.listdir():
        if f in EXCLUDE_FILES:
            continue
        try:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)
        except Exception as e:
            print(f"❌ Не удалось удалить {f}: {e}")

# === Обновление с прогресс-баром ===
def install_update():
    print("🧹 Удаление старых файлов...")
    delete_old_files()

    print("🔄 Подсчёт файлов...")
    total = count_files(getUrl(GITHUB_FOLDER_LINK))

    print("⬇️ Загрузка новых файлов...")
    progress_ui = ProgressDownloader(total)
    download_folder_contents(getUrl(GITHUB_FOLDER_LINK), DOWNLOAD_FOLDER, progress_ui)
    progress_ui.close()

    print("✅ Обновление завершено. Перезапуск...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# === Tkinter окно ===
def prompt_user_update(local, remote):
    def on_yes():
        root.destroy()
        install_update()

    def on_no():
        root.destroy()
        print("⏩ Продолжение без обновления...")

    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno(
        "Обновление доступно",
        f"Доступна новая версия: {remote}\nВаша версия: {local}\n\nУстановить обновление?"
    )
    if result:
        on_yes()
    else:
        on_no()

# === Основная проверка ===
def check_for_update():
    print("🔍 Проверка обновлений...")
    local = get_local_version()
    remote = get_remote_version()
    if remote and compare_versions(local, remote):
        print(f"📦 Доступна новая версия {remote} (текущая: {local})")
        prompt_user_update(local, remote)
    else:
        print("✅ У вас последняя версия.")

if __name__ == "__main__":
    check_for_update()
