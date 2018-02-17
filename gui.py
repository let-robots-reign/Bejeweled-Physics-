import pygame

screen_color = pygame.Color('white')


class GUI:
    def __init__(self):
        self.elements = []

    def clear(self):
        self.elements.clear()

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)


class Label:
    def __init__(self, rect, text, text_color=pygame.Color('black'), background_color=pygame.Color('white'),
                 font_size=None, x=None, y=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.text_color = text_color
        self.background_color = background_color
        self.x = self.rect.x + 2 if x is None else x
        self.y = self.rect.y + 2 if y is None else y
        if font_size is None:
            # Calculating the font's size
            self.font = pygame.font.Font(None, self.rect.height - 4)
        else:
            self.font = pygame.font.Font(None, font_size)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        if self.background_color == -1:
            surface.fill(screen_color, self.rect)
        else:
            surface.fill(self.background_color, self.rect)
        words = [word.split(' ') for word in self.text.splitlines()]  # 2D array where each row is a list of words.
        space = self.font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = self.x, self.y
        for line in words:
            for word in line:
                word_surface = self.font.render(word, 1, self.text_color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width - 100:
                    x = self.x  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = self.x  # Reset the x.
            y += word_height  # Start on new row.
        # self.rendered_text = self.font.render(self.text, 1, self.text_color)
        # self.rendered_rect = self.rendered_text.get_rect(x=self.x, y=self.y)
        # surface.blit(self.rendered_text, self.rendered_rect)


class Button(Label):
    def __init__(self, rect, text, text_color=pygame.Color('black'), background_color=pygame.Color('blue'),
                 font_size=None):
        super().__init__(rect, text, font_size)
        self.font_color = text_color
        self.bgcolor = background_color
        # при создании кнопка не нажата
        self.pressed = False
        self.illumination = False  # подсвечивание

    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 5, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 7, centery=self.rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)
        if self.illumination:
            temp_s = pygame.Surface((self.rect.width, self.rect.height))
            temp_s.set_alpha(190)  # устанавливаем прозрачность
            temp_s.fill(pygame.Color('lightblue'))
            surface.blit(temp_s, (self.rect.x, self.rect.y))

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:  # если мышь движется
            if self.rect.collidepoint(event.pos):  # и попадает в область кнопки
                self.illumination = True
            else:
                self.illumination = False
