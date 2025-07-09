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
    
import xml.etree.ElementTree as ET
import pygame
import os

from lib.engin import Button, Label, ProgressBar, Checkbox, Dropdown, Radio, Image, InputField, Slider

def load_ui_from_folder(design_folder, default_font=None):
    xml_path = os.path.join(design_folder, "ui.xml")
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Не найден ui.xml в {design_folder}")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    elements = []
    element_by_id = {}

    for el in root:
        x = int(el.get('x', 0))
        y = int(el.get('y', 0))
        width = int(el.get('width', 100))
        height = int(el.get('height', 30))
        rect = pygame.Rect(x, y, width, height)

        font_size = int(el.get('font_size', 18))
        font = pygame.font.Font(None, font_size) if default_font is None else default_font

        tag = el.tag.lower()
        element_id = el.get('id', None)

        ui_element = None

        if tag == "label":
            text = el.get("text", "")
            ui_element = Label(rect, text=text, font=font)

        elif tag == "button":
            text = el.get("text", "")
            ui_element = Button(rect, text=text, font=font)
            img_src = el.get("image")
            if img_src:
                img_path = os.path.join(design_folder, img_src)
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    ui_element.image = img

        elif tag == "progressbar":
            value = int(el.get("value", 0))
            max_value = int(el.get("max", 100))
            visible = eval(el.get("visible", 'True'))
            show_percent = el.get("show_percent", "1") == "1"
            ui_element = ProgressBar(rect, value=value, max_value=max_value,
                                     font=font, show_percent=show_percent, visible=visible)

        elif tag == "checkbox":
            text = el.get("text", "")
            ui_element = Checkbox(rect, text=text, font=font)

        elif tag == "dropdown":
            items = el.get("items", "")
            options = [i.strip() for i in items.split(",")]
            ui_element = Dropdown(rect, options=options, font=font)

        elif tag == "radio":
            text = el.get("text", "")
            group = el.get("group", "default")
            ui_element = Radio(rect, text=text, font=font, group=group)

        elif tag == "image":
            path = el.get("src", "")
            full_path = os.path.join(design_folder, path)
            try:
                img = pygame.image.load(full_path).convert_alpha()
                ui_element = Image(rect, image=img)
            except:
                print(f"⚠ Не удалось загрузить изображение: {full_path}")

        elif tag == "inputfield":
            placeholder = el.get("placeholder", "")
            ui_element = InputField(
                rect,
                text="",
                font=font,
                text_color=(0, 0, 0),
                bg_color=(255, 255, 255),
                caret_color=(0, 0, 0),
                padding=5,
                shadow=False,
                outline_radius=2,
                outline_color=(100, 100, 100)
            )
            ui_element.placeholder = placeholder

        elif tag == "slider":
            min_v = int(el.get("min", 0))
            max_v = int(el.get("max", 100))
            val = int(el.get("value", min_v))
            ui_element = Slider(
                rect,
                min_value=min_v,
                max_value=max_v,
                value=val,
                shadow=False,
                outline_radius=2,
                outline_color=(100, 100, 100)
            )

        # Применяем ID, если есть
        if ui_element:
            if element_id:
                ui_element.id = element_id
                element_by_id[element_id] = ui_element
            elements.append(ui_element)

    return elements, element_by_id
