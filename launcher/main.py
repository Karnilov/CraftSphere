import update_checker
update_checker.check_for_update()
import os
import psutil
import requests
import pygame
import minecraft_launcher_lib
from ui_loader import load_ui_from_folder
from threading import Thread
from subprocess import Popen, run
from minecraft_launcher_lib.utils import get_minecraft_directory
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command
from minecraft_launcher_lib.forge import install_forge_version
import tkinter as tk
from tkinter import messagebox

pygame.init()
screen = pygame.display.set_mode((600, 270), pygame.NOFRAME)
clock = pygame.time.Clock()

design_folder = "assets/v1"
elements, elementsID = load_ui_from_folder(design_folder)

reinstall_checkbox  = elementsID['Reinstall']
TotalPrograss       = elementsID['TotalPrograss']
TaskPrograss        = elementsID['TaskPrograss']
dropdownsVersion    = elementsID['SelectVersion']
buttonRun           = elementsID['Run']
SelectMemory        = elementsID['SelectMemory']
CurentMemory        = elementsID['CurentMemory']
Username            = elementsID['Username']

total_mods = 0
count_mods = 0

versions = {
    'Анархия с донатами': {'version': '1.20.1', 'forge': False},
    'Анархия без доната': {'version': '1.20.1', 'forge': False},
    'Техно': {'version': '1.12.2', 'forge': True, 'modsURL': 'https://github.com/Karnilov/CraftSphere/tree/main/Techno'},
    'Bad wars': {'version': '1.20.1', 'forge': False},
    'Королевство с модами': {'version': '1.20.1', 'forge': True, 'modsURL': 'https://github.com/Karnilov/CraftSphere/tree/main/Kingdom'},
    'Королевства без модов': {'version': '1.20.1', 'forge': False},
    'Королевства V2.0': {'version': '1.19.2', 'forge': True, 'modsURL': 'https://github.com/Karnilov/CraftSphere/tree/main/Kingdom%20V2.0'}
}

def set_status(text):
    TaskPrograss.lable = text
    print('[STATUS]: '+text)
def set_progress(value):
    TaskPrograss.value = value
def set_max(value):
    TaskPrograss.max_value = value
def show_notification():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Уведомление", "Введите имя пользователя!!!")
    root.destroy()
def get_total_ram_mb():
    vm = psutil.virtual_memory()
    return int(vm.total / (1024 * 1024))
def getUrl(link):
    lk = link.split('/')
    owner, repo = lk[3], lk[4]
    path = '/'.join(lk[7:])
    return f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
def count_folder_contents(folder_url):
    try:
        r = requests.get(folder_url)
        r.raise_for_status()
        items = r.json()
    except Exception:
        return 0
    count = 0
    for it in items:
        if it['type'] == 'file':
            count += 1
        elif it['type'] == 'dir':
            count += count_folder_contents(it['url'])
    return count
def download_file(file_url, folder_path):
    response = requests.get(file_url)
    filename = os.path.join(folder_path, os.path.basename(file_url))
    os.makedirs(folder_path, exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(response.content)
def download_folder_contents(folder_url, folder_path):
    global count_mods
    try:
        r = requests.get(folder_url)
        r.raise_for_status()
        items = r.json()
    except Exception as e:
        print(f"Error fetching folder: {e}")
        return
    count_mods = 0
    set_max(total_mods)
    for item in items:
        count_mods += 1
        set_status(item['name'])
        set_progress(count_mods)
        if item['type'] == 'file':
            download_file(item['download_url'], folder_path)
        elif item['type'] == 'dir':
            new_folder = os.path.join(folder_path, item['name'])
            download_folder_contents(item['url'], new_folder)

callback = {
    "setStatus": set_status,
    "setProgress": set_progress,
    "setMax": set_max
}

def run():
    if Username.text == '':
        show_notification()
        return
    global total_mods
    TotalPrograss.visible = True
    TaskPrograss.visible = True
    try:
        mc_dir = get_minecraft_directory().replace('minecraft', 'CraftSphere')
        selected = dropdownsVersion.options[dropdownsVersion.selected]
        info = versions[selected]
        vid = info['version']

        if info.get('forge'): TotalPrograss.max_value = 4
        else: TotalPrograss.max_value = 2

        total_mods = count_folder_contents(getUrl(info.get('modsURL', '')) ) if info.get('forge') else 0

        if reinstall_checkbox.checked:
            TotalPrograss.lable = "Installing Minecraft..."
            install_minecraft_version(versionid=vid, minecraft_directory=mc_dir, callback=callback)
            TotalPrograss.value += 1
        else:
            TotalPrograss.lable = "Skipping Minecraft installation"
            TotalPrograss.value += 1

        if info.get('forge'):
            fv = minecraft_launcher_lib.forge.find_forge_version(vid)
            if fv:
                TotalPrograss.lable = f"Installing Forge {fv}..."
                install_forge_version(fv, mc_dir, callback=callback)
                TotalPrograss.value += 1
                vid = fv.replace(vid, vid + "-forge")
                TotalPrograss.lable = "Downloading mods..."
                download_folder_contents(getUrl(info['modsURL']), os.path.join(mc_dir, 'mods'))
                TotalPrograss.value += 1

        # финальный запуск
        TotalPrograss.lable = "Launching Minecraft..."

        # JVM параметры: только наша настройка
        total_ram = get_total_ram_mb()
        max_ram = min(int(total_ram * 0.75), 4096)



        options = {
            "username": Username.text,
            "jvmArguments":[f"-Xmx{int(SelectMemory.value)}M"],
            "server": "craftsphere.serveftp.com",
            "port": "25565",
        }

        TotalPrograss.value += 1
        cmd = get_minecraft_command(
            version=vid,
            minecraft_directory=mc_dir,
            options=options
        )
        Popen(cmd, shell=True)
        TotalPrograss.visible = False
        TaskPrograss.visible = False

    except Exception as e:
        print(f"[ERROR_KoDer] {e}")
        set_status("An error occurred. Check console for details.")

buttonRun.callback = lambda: Thread(target=run, daemon=True).start()
SelectMemory.min = 0
SelectMemory.max = get_total_ram_mb()
SelectMemory.value = 4096

running = True
while running:
    screen.fill((240, 240, 240))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not dropdownsVersion.expanded:
            for el in elements:
                el.handle_event(event)
        else:
            dropdownsVersion.handle_event(event)

    CurentMemory.text = str(int(SelectMemory.value))

    for el in elements:
        el.update()
    dropdowns = [el for el in elements if el.__class__.__name__.lower() == "dropdown"]
    others    = [el for el in elements if el.__class__.__name__.lower() != "dropdown"]
    for el in others:
        el.draw(screen)
    for dd in dropdowns:
        dd.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()