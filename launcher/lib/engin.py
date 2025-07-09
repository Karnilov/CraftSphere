import pygame
pygame.init()

class UIElement:
    def __init__(self, rect, font=None, shadow=False, outline_radius=0, outline_color=(0,0,0), font_name=pygame.font.get_default_font(), visible = True):
        self.rect = pygame.Rect(rect)
        self.font = font or pygame.font.Font(font_name, 20)
        self.visible = visible
        self.shadow = shadow
        self.outline_radius = outline_radius
        self.outline_color = outline_color

    def draw_shadow(self, surface):
        if self.shadow:
            shadow_rect = self.rect.move(4, 4)
            pygame.draw.rect(surface, (50, 50, 50, 50), shadow_rect, border_radius=8)

    def draw_outline(self, surface, border_radius=8, width=2):
        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius*2, self.outline_radius*2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, width, border_radius=border_radius)

    def draw(self, surface):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        # Пустой метод, чтобы не было ошибки у наследников без update
        pass

    def set_font(self, font):
        self.font = font
class Label(UIElement):
    def __init__(self, rect, text, font=None, color=(0,0,0), **kwargs):
        super().__init__(rect, font, **kwargs)
        self.text = text
        self.color = color

    def draw(self, surface):
        if not self.visible:
            return
        text_surf = self.font.render(self.text, True, self.color)
        surface.blit(text_surf, self.rect.topleft)
        # Labels обычно без тени и обводки
class Button(UIElement):
    def __init__(self, rect, text="", font=None, bg_color=(200, 200, 200), text_color=(0, 0, 0),
                 shadow=False, outline_radius=0, outline_color=(0, 0, 0)):
        super().__init__(rect, font, shadow, outline_radius, outline_color)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.image = None
        self.callback = None

        self.hovered = False
        self.pressed = False

        self.anim_scale = 1.0
        self.target_scale = 1.0
        self.anim_speed = 0.1

    def draw(self, surface):
        if not self.visible:
            return

        # --- Scale animation ---
        scaled_rect = self.rect.inflate(
            self.rect.width * (self.anim_scale - 1),
            self.rect.height * (self.anim_scale - 1)
        )
        scaled_rect.center = self.rect.center

        if self.image:
            img_rect = self.image.get_rect(center=scaled_rect.center)
            surface.blit(self.image, img_rect)

            if self.text:
                text_surf = self.font.render(self.text, True, self.text_color)
                text_rect = text_surf.get_rect(center=scaled_rect.center)
                surface.blit(text_surf, text_rect)
            return

        if self.shadow:
            shadow_rect = scaled_rect.move(4, 4)
            pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=12)

        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, scaled_rect, border_radius=12)

        if self.outline_radius > 0:
            outline_rect = scaled_rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=12)

        if self.text:
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=scaled_rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
            self.pressed = False

    def update(self):
        # Определяем целевой масштаб
        if self.pressed:
            self.target_scale = 0.95
        elif self.hovered:
            self.target_scale = 1.05
        else:
            self.target_scale = 1.0

        # Плавно интерполируем
        self.anim_scale += (self.target_scale - self.anim_scale) * self.anim_speed

    def set_callback(self, fn):
        self.callback = fn
class ProgressBar(UIElement):
    def __init__(self, rect, max_value=100, value=0, font=None,
                 bg_color=(230, 230, 230), fill_color=(100, 180, 100),
                 text_color=(0, 0, 0), show_percent=True,
                 shadow=False, outline_radius=0, outline_color=(0, 0, 0), lable = None, visible=True):
        super().__init__(rect, font, shadow, outline_radius, outline_color, visible=visible)
        self.max_value = max_value
        self.value = value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.text_color = text_color
        self.show_percent = show_percent
        self.border_radius = 12
        self.lable = lable

    def set_value(self, val):
        self.value = max(0, min(val, self.max_value))

    def draw(self, surface):
        if not self.visible:
            return

        if self.shadow:
            shadow_rect = self.rect.move(4, 4)
            pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=self.border_radius)

        if self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.border_radius)

        fill_width = int((self.value / self.max_value) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)

        pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=self.border_radius)

        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=self.border_radius)

        # Текст (с процентами или текущим/макс)
        if self.show_percent:
            percent = int((self.value / self.max_value) * 100)
            if self.lable:
                label = f"{self.lable+' : '+str(percent)}%"
            else:
                label = f"{percent}%"
        else:
            label = f"{self.value}/{self.max_value}"

        text_surf = self.font.render(label, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self):
        pass  # можно добавить анимацию значения если нужно
class Checkbox(UIElement):
    def __init__(self, rect, text="", font=None, checked=False, shadow=False,
                 outline_radius=0, outline_color=(0, 0, 0)):
        super().__init__(rect, font, shadow, outline_radius, outline_color)
        self.text = text
        self.checked = checked
        self.border_radius = 8
        self.animation_progress = 1.0 if checked else 0.0
        self.animation_speed = 0.15  # Скорость анимации

    def draw(self, surface):
        if not self.visible:
            return

        # Обводка
        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=self.border_radius)

        # Фон чекбокса
        pygame.draw.rect(surface, (230, 230, 230), self.rect, border_radius=self.border_radius)

        # Прямоугольник галочки
        box_size = min(self.rect.height - 10, 30)
        box_rect = pygame.Rect(self.rect.x + 8, self.rect.y + (self.rect.height - box_size) // 2,
                               box_size, box_size)
        pygame.draw.rect(surface, (180, 180, 180), box_rect, border_radius=5)

        # Заливка галочки (анимированная)
        if self.animation_progress > 0:
            fill_rect = box_rect.inflate(-4, -4)
            alpha = int(self.animation_progress * 255)
            fill_surf = pygame.Surface(fill_rect.size, pygame.SRCALPHA)
            fill_surf.fill((60, 150, 60, alpha))
            surface.blit(fill_surf, fill_rect.topleft)

        # Текст рядом
        if self.text and self.font:
            text_surf = self.font.render(self.text, True, (0, 0, 0))
            surface.blit(text_surf, (box_rect.right + 10, self.rect.centery - text_surf.get_height() // 2))

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.toggle()

    def toggle(self):
        self.checked = not self.checked

    def is_checked(self):
        return self.checked

    def update(self):
        # Плавная анимация
        target = 1.0 if self.checked else 0.0
        if abs(self.animation_progress - target) > 0.01:
            direction = 1 if self.animation_progress < target else -1
            self.animation_progress += self.animation_speed * direction
            self.animation_progress = max(0.0, min(1.0, self.animation_progress))
class Dropdown(UIElement):
    def __init__(self, rect, options, font=None, shadow=False, outline_radius=0, outline_color=(0,0,0), max_visible_options=3):
        super().__init__(rect, font, shadow, outline_radius, outline_color)
        self.options = options
        self.selected = 0
        self.expanded = False
        self.option_height = self.rect.height
        self.callback = None

        self.anim_height = 0
        self.anim_speed = 15

        self.max_visible_options = max_visible_options
        self.scroll_offset = 0

    def draw(self, surface):
        if not self.visible:
            return

        if self.shadow:
            shadow_rect = self.rect.move(3, 3)
            pygame.draw.rect(surface, (50, 50, 50, 100), shadow_rect, border_radius=12)

        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=12)

        # Отображение текущего значения
        text_surf = self.font.render(self.options[self.selected], True, (0, 0, 0))
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        # Стрелка
        arrow_center = (self.rect.right - 15, self.rect.centery)
        pygame.draw.polygon(surface, (0, 0, 0), [
            (arrow_center[0] - 5, arrow_center[1] - 3),
            (arrow_center[0] + 5, arrow_center[1] - 3),
            (arrow_center[0], arrow_center[1] + 4)
        ])

        # Выпадающий список
        if self.anim_height > 0:
            clip_rect = pygame.Rect(self.rect.left, self.rect.bottom, self.rect.width, self.anim_height)
            surface.set_clip(clip_rect)

            visible_options = min(self.max_visible_options, len(self.options))
            for i in range(self.scroll_offset, self.scroll_offset + visible_options):
                if i >= len(self.options):
                    break
                y = self.rect.bottom + (i - self.scroll_offset) * self.option_height
                option_rect = pygame.Rect(self.rect.left, y, self.rect.width, self.option_height)
                pygame.draw.rect(surface, (220, 220, 220), option_rect)
                opt_text = self.font.render(self.options[i], True, (0, 0, 0))
                surface.blit(opt_text, (option_rect.x + 5, option_rect.y + (self.option_height - opt_text.get_height()) // 2))

            # Скроллбар
            if len(self.options) > self.max_visible_options:
                scrollbar_height = self.anim_height
                bar_height = max(10, int(scrollbar_height * (self.max_visible_options / len(self.options))))
                scroll_y = int(scrollbar_height * (self.scroll_offset / len(self.options)))
                pygame.draw.rect(surface, (180, 180, 180), (self.rect.right - 6, self.rect.bottom, 6, scrollbar_height))
                pygame.draw.rect(surface, (120, 120, 120), (self.rect.right - 6, self.rect.bottom + scroll_y, 6, bar_height))

            surface.set_clip(None)

        # Обводка
        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=12)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.expanded:
                for i in range(self.scroll_offset, self.scroll_offset + self.max_visible_options):
                    if i >= len(self.options):
                        break
                    option_rect = pygame.Rect(self.rect.left, self.rect.bottom + (i - self.scroll_offset) * self.option_height, self.rect.width, self.option_height)
                    if option_rect.collidepoint(event.pos):
                        self.selected = i
                        self.expanded = False
                        if self.callback:
                            self.callback(self.options[self.selected])
                        return
                if not self.rect.collidepoint(event.pos):
                    self.expanded = False
            else:
                if self.rect.collidepoint(event.pos):
                    self.expanded = True

        # Прокрутка
        if event.type == pygame.MOUSEWHEEL:
            if self.expanded:
                max_scroll = max(0, len(self.options) - self.max_visible_options)
                self.scroll_offset = max(0, min(self.scroll_offset - event.y, max_scroll))

    def update(self):
        target_height = min(self.max_visible_options, len(self.options)) * self.option_height if self.expanded else 0
        if self.anim_height < target_height:
            self.anim_height += self.anim_speed
            if self.anim_height > target_height:
                self.anim_height = target_height
        elif self.anim_height > target_height:
            self.anim_height -= self.anim_speed
            if self.anim_height < target_height:
                self.anim_height = target_height

    def set_callback(self, fn):
        self.callback = fn
class Radio(UIElement):
    def __init__(self, rect, group, selected=False, font=None, shadow=False, outline_radius=0, outline_color=(0,0,0)):
        super().__init__(rect, font, shadow, outline_radius, outline_color)
        self.group = group
        self.selected = selected
        self.callback = None
        self.anim_progress = 1 if selected else 0
        self.anim_speed = 0.15

    def draw(self, surface):
        if not self.visible:
            return

        if self.shadow:
            shadow_rect = self.rect.move(3,3)
            pygame.draw.ellipse(surface, (50,50,50,100), shadow_rect)

        pygame.draw.ellipse(surface, (0,0,0), self.rect, 2)

        if self.anim_progress > 0:
            inner_radius = int((self.rect.width//2 - 4) * self.anim_progress)
            center = self.rect.center
            pygame.draw.ellipse(surface, (0,0,0), (center[0] - inner_radius, center[1] - inner_radius, inner_radius*2, inner_radius*2))

        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius*2, self.outline_radius*2)
            pygame.draw.ellipse(surface, self.outline_color, outline_rect, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                for btn in self.group:
                    btn.selected = False
                self.selected = True
                if self.callback:
                    self.callback(self.selected)

    def update(self):
        target = 1 if self.selected else 0
        if self.anim_progress < target:
            self.anim_progress += self.anim_speed
            if self.anim_progress > target:
                self.anim_progress = target
        elif self.anim_progress > target:
            self.anim_progress -= self.anim_speed
            if self.anim_progress < target:
                self.anim_progress = target

    def set_callback(self, fn):
        self.callback = fn
class Image(UIElement):
    def __init__(self, rect, image=None, shadow=False, outline_radius=0, outline_color=(0, 0, 0)):
        super().__init__(rect, font=None, shadow=shadow, outline_radius=outline_radius, outline_color=outline_color)
        self.image = image
        self.border_radius = 12

    def draw(self, surface):
        if not self.visible or self.image is None:
            return

        if self.shadow:
            shadow_rect = self.rect.move(4, 4)
            pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=self.border_radius)

        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=self.border_radius)

        surface.blit(pygame.transform.smoothscale(self.image, (self.rect.width, self.rect.height)), self.rect)

    def update(self):
        pass
class InputField(UIElement):
    def __init__(self, rect, text="", font=None, text_color=(0, 0, 0),
                 bg_color=(255, 255, 255), caret_color=(0, 0, 0), padding=5,
                 shadow=False, outline_radius=0, outline_color=(0, 0, 0)):
        super().__init__(rect, font, shadow, outline_radius, outline_color)
        self.text = text
        self.text_color = text_color
        self.bg_color = bg_color
        self.caret_color = caret_color
        self.padding = padding
        self.active = False
        self.caret_pos = len(text)
        self.blink = True
        self.blink_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.caret_pos > 0:
                    self.text = self.text[:self.caret_pos - 1] + self.text[self.caret_pos:]
                    self.caret_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.caret_pos < len(self.text):
                    self.text = self.text[:self.caret_pos] + self.text[self.caret_pos + 1:]
            elif event.key == pygame.K_LEFT:
                self.caret_pos = max(0, self.caret_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.caret_pos = min(len(self.text), self.caret_pos + 1)
            elif event.key == pygame.K_HOME:
                self.caret_pos = 0
            elif event.key == pygame.K_END:
                self.caret_pos = len(self.text)
            else:
                # добавляем символ
                char = event.unicode
                if char:
                    self.text = self.text[:self.caret_pos] + char + self.text[self.caret_pos:]
                    self.caret_pos += 1

    def update(self):
        # мигалка курсора
        self.blink_timer += 1
        if self.blink_timer > 30:
            self.blink = not self.blink
            self.blink_timer = 0

    def draw(self, surface):
        if not self.visible:
            return
        # фон
        if self.shadow:
            shadow_rect = self.rect.move(4, 4)
            pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=12)
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=12)
        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=12)
        # текст
        txt_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(txt_surf,
                     (self.rect.x + self.padding, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))
        # курсор
        if self.active and self.blink:
            # вычисляем позицию курсора
            pre_text = self.text[:self.caret_pos]
            width = self.font.size(pre_text)[0]
            x = self.rect.x + self.padding + width
            y1 = self.rect.y + 5
            y2 = self.rect.y + self.rect.height - 5
            pygame.draw.line(surface, self.caret_color, (x, y1), (x, y2), 2)
class Slider(UIElement):
    def __init__(self, rect, min_value=0, max_value=100, value=0,
                 bg_color=(200, 200, 200), fill_color=(100, 180, 100),
                 handle_color=(50, 50, 50), handle_radius=8,
                 shadow=False, outline_radius=0, outline_color=(0, 0, 0)):
        super().__init__(rect, None, shadow, outline_radius, outline_color)
        self.min = min_value
        self.max = max_value
        self.value = value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.handle_color = handle_color
        self.handle_radius = handle_radius
        self.dragging = False
        self.callback = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # попали ли по ручке?
            hx = self._handle_x()
            hy = self.rect.centery
            if pygame.Vector2(event.pos).distance_to((hx, hy)) <= self.handle_radius:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # вычисляем новое значение по X
            rel = (event.pos[0] - self.rect.x) / self.rect.width
            self.value = max(self.min, min(self.max, self.min + rel * (self.max - self.min)))
            if self.callback:
                self.callback(self.value)

    def _handle_x(self):
        # позиция ручки по X
        frac = (self.value - self.min) / (self.max - self.min)
        return int(self.rect.x + frac * self.rect.width)

    def draw(self, surface):
        if not self.visible:
            return
        # фон
        if self.shadow:
            shadow_rect = self.rect.move(4, 4)
            pygame.draw.rect(surface, (50, 50, 50), shadow_rect, border_radius=12)
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=12)
        # заполнение
        fill_rect = pygame.Rect(self.rect.x, self.rect.y,
                                int((self.value - self.min) / (self.max - self.min) * self.rect.width),
                                self.rect.height)
        pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=12)
        # обводка
        if self.outline_radius > 0:
            outline_rect = self.rect.inflate(self.outline_radius * 2, self.outline_radius * 2)
            pygame.draw.rect(surface, self.outline_color, outline_rect, 2, border_radius=12)
        # ручка
        hx = self._handle_x()
        hy = self.rect.centery
        pygame.draw.circle(surface, self.handle_color, (hx, hy), self.handle_radius)

    def set_callback(self, fn):
        self.callback = fn