import requests
import os
import shutil
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

GITHUB_RAW = "https://raw.githubusercontent.com/Karnilov/CraftSphere/main/launcher/"
GITHUB_TREE = "https://github.com/Karnilov/CraftSphere/tree/main/launcher"
LOCAL_VERSION_FILE = "version.txt"
EXCLUDE_FILES = {os.path.basename(__file__), LOCAL_VERSION_FILE, "update_checker.py"}  # Не удалять эти файлы

def get_local_version():
    try:
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.0.0"

def get_remote_version():
    try:
        response = requests.get(GITHUB_RAW + "version.txt")
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"❌ Не удалось получить удалённую версию: {e}")
        return None

def compare_versions(local, remote):
    return tuple(map(int, remote.split("."))) > tuple(map(int, local.split(".")))

def list_files_in_repo_folder():
    try:
        response = requests.get(GITHUB_TREE)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        files = []
        for link in soup.select("div[role='rowheader'] a[href]"):
            href = link["href"]
            if "/Karnilov/CraftSphere/blob/main/launcher/" in href:
                filename = href.split("/")[-1]
                files.append(filename)
        return files
    except Exception as e:
        print(f"❌ Не удалось получить список файлов: {e}")
        return []

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

def download_files(files):
    for file in files:
        url = GITHUB_RAW + file
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file, "wb") as f:
                f.write(response.content)
            print(f"✅ Загружен файл: {file}")
        except Exception as e:
            print(f"❌ Ошибка при загрузке {file}: {e}")

def install_update():
    print("🧹 Удаление старых файлов...")
    delete_old_files()
    print("⬇️ Загрузка новых файлов...")
    files = list_files_in_repo_folder()
    download_files(files)
    print("✅ Обновление завершено. Перезапуск...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def prompt_user_update(local, remote):
    def on_yes():
        root.destroy()
        install_update()

    def on_no():
        root.destroy()
        print("⏩ Продолжение без обновления...")

    root = tk.Tk()
    root.withdraw()  # Скрыть основное окно
    root.after(0, lambda: show_message(root, local, remote, on_yes, on_no))
    root.mainloop()

def show_message(root, local, remote, on_yes, on_no):
    result = messagebox.askyesno(
        "Доступно обновление",
        f"Доступна новая версия: {remote}\nВаша версия: {local}\n\nУстановить обновление?"
    )
    if result:
        on_yes()
    else:
        on_no()

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
