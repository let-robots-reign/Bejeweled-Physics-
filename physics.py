import pygame
import random
import sys
from gui import *

pygame.init()
width, height = 1200, 950
size = width, height
screen = pygame.display.set_mode(size)
symbols = {0: 'data/symbol0.png', 1: 'data/symbol1.png', 2: 'data/symbol2.png', 3: 'data/symbol3.png',
           4: 'data/symbol4.png', 5: 'data/symbol5.png', 6: 'data/symbol6.png', 7: 'data/symbol7.png',
           8: 'data/symbol8.png', 9: 'data/symbol9.png', 10: 'data/symbol10.png', 11: 'data/symbol11.png',
           12: 'data/symbol12.png'}  # convert board values to images

numbers_to_letters = {-1: 'X', 0: '*', 1: '/', 2: 'π', 3: 'm', 4: 'g', 5: 'I', 6: 'U', 7: 'S', 8: 't', 9: 'v', 10: 'a',
                      11: 'V', 12: 'p'}  # convert board values to letters

formulas = ['m*g', 'U/I', 'S/v', 'S/t', 'v*t', 'v/t', 'a*t', 'p*V', 'm/V', 'm/p', 'm*a', 'm*v']  # formulas to be in the game

game_sounds = {'swap': pygame.mixer.Sound('data/swap.wav'), 'match': [pygame.mixer.Sound('data/match1.wav'),
              pygame.mixer.Sound('data/match2.wav'), pygame.mixer.Sound('data/match3.wav'),
              pygame.mixer.Sound('data/match4.wav'), pygame.mixer.Sound('data/match5.wav')]}  # sounds to be played after an action


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.frame_index = 0
        self.image = pygame.image.load('data/atom_animation/atom%s.gif' % self.frame_index)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clock = pygame.time.Clock()
        self.fps = 30

    def update(self):
        self.frame_index = (self.frame_index + 1) % 40  # 40 - number of frames
        self.image = pygame.image.load('data/atom_animation/atom%s.gif' % self.frame_index)
        self.clock.tick(self.fps)


class LangButton(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.image.load('data/eng.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False

    def update(self):
        if self.pressed:
            print('pressed')
            self.image = pygame.image.load('data/rus.png')
        else:
            print('unpressed')
            self.image = pygame.image.load('data/eng.png')

    def get_event(self, event):
        if self.rect.collidepoint(event.pos):
            print(1)
            self.pressed = not self.pressed


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[-1 for _ in range(width)] for _ in range(height)]  # -1 is an empty cell
        self.left = 100
        self.top = 40
        self.cell_size = 64


class Bejeweled(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pressed = ()  # coords of the pressed cell
        self.score = 0
        self.swaps = -1  # the first swap doesn't take off points
        self.font = pygame.font.Font(None, 40)
        self.score_text = None
        self.timer_text = None
        self.timer = 0
        self.dt = 0
        self.clock = None  # clock initializing is in game()

        for i in range(30):  # 30 multiplications
            x, y = self.random_coords()
            while self.board[y][x] != -1:  # to avoid repetition
                x, y = self.random_coords()
            self.board[y][x] = 0

        for i in range(15):  # 15 divisions
            x, y = self.random_coords()
            while self.board[y][x] != -1:  # to avoid repetition
                x, y = self.random_coords()
            self.board[y][x] = 1

        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == -1:
                    self.board[y][x] = random.randint(2, len(symbols) - 1)  # random value from the list

    def random_coords(self):
        return random.randint(0, self.width - 1), random.randint(0, self.height - 1)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        if cell_x < 0 or cell_x > self.width:
            return None
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_y < 0 or cell_y > self.height:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def shift_tiles_down(self):
        board = list(map(list, zip(*self.board)))  # zipping the board to iterate its columns
        for y in range(len(board)):
            if -1 in board[y]:
                # shifting
                board[y] = [-1] * board[y].count(-1) + board[y][:board[y].index(-1)] + board[y][board[y].index(-1) + board[y].count(-1):]
                for i in range(board[y].count(-1)):
                    board[y][i] = random.randint(0, len(symbols) - 1)  # refilling
        board = list(map(list, zip(*board)))  # zip the board back
        return board

    def mainloop(self):
        rotated_board = list(map(list, zip(*self.board)))  # zipping the board to iterate its columns
        for y in range(self.height):
            sy = ''.join([numbers_to_letters[x] for x in self.board[y]])
            sx = ''.join([numbers_to_letters[x] for x in rotated_board[y]])
            for formula in formulas:  # finding vertical matches
                if formula in sx:
                    sound_index = random.randint(0, 4)
                    game_sounds['match'][sound_index].play()
                    self.score += 10 * len(formula)
                    self.timer += 5
                    self.swaps = -1
                    # pygame.draw.rect(screen, pygame.Color('red'),
                    #                  (x * self.cell_size + self.left,
                    #                   sx.find(formula) * self.cell_size + self.top,
                    #                   self.cell_size, self.cell_size * len(formula)), 3)
                    for i in range(len(formula)):
                        self.board[sx.find(formula) + i][y] = -1

                elif formula in sy:
                    sound_index = random.randint(0, 4)
                    game_sounds['match'][sound_index].play()
                    self.score += 10 * len(formula)
                    self.timer += 5
                    self.swaps = -1
                    # pygame.draw.rect(screen, pygame.Color('red'),
                    #                  (sy.find(formula) * self.cell_size + self.left,
                    #                   y * self.cell_size + self.top,
                    #                   self.cell_size * len(formula), self.cell_size), 3)
                    for i in range(len(formula)):
                        self.board[y][sy.find(formula) + i] = -1

            for x in range(self.width):
                if self.board[y][x] != -1:  # blitting the picture
                    img = pygame.image.load(symbols[self.board[y][x]])
                    screen.blit(img, (x * self.cell_size + self.left, y * self.cell_size + self.top))
                pygame.draw.rect(screen, pygame.Color('white'),  # drawing cells
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)

        if self.pressed:  # framing of the pressed cell
            pygame.draw.rect(screen, pygame.Color('red'),
                             (self.pressed[0] * self.cell_size + self.left, self.pressed[1] * self.cell_size + self.top,
                              self.cell_size, self.cell_size), 3)

        self.score_text = self.font.render('Score: %d' % self.score, 1, pygame.Color('black'))
        self.timer_text = self.font.render('Time: %d' % self.timer, 1, pygame.Color('black'))
        screen.blit(self.score_text, (900, 55))
        screen.blit(self.timer_text, (900, 119))

        self.board = self.shift_tiles_down()  # shifting the tiles

        if self.timer - self.dt > 0:
            self.timer -= self.dt
        else:
            self.pressed = ()
            game_over()

        self.dt = self.clock.tick(1000) / 1000

    def on_click(self, cell):
        if cell == self.pressed:
            self.pressed = ()  # second pressing makes the cell inactive
        else:
            if self.pressed:
                # swapping
                self.swaps += 1
                self.score -= self.swaps
                if abs(cell[0] - self.pressed[0]) <= 1 and abs(cell[1] - self.pressed[1]) <= 1 \
                        and (abs(cell[0] - self.pressed[0]) == 0 or abs(cell[1] - self.pressed[1]) == 0):
                    game_sounds['swap'].play()
                    self.board[self.pressed[1]][self.pressed[0]], self.board[cell[1]][cell[0]] = self.board[cell[1]][ cell[0]], self.board[self.pressed[1]][self.pressed[0]]
                    self.pressed = ()  # cell is inactive
                else:
                    self.pressed = ()  # cell is inactive after swapping
            else:
                self.pressed = cell  # cell is active


def pre_check_matches(board):  # eliminating all matches before starting
    rotated_board = list(map(list, zip(*board)))
    for y in range(len(board)):
        sy = ''.join([numbers_to_letters[x] for x in board[y]])
        sx = ''.join([numbers_to_letters[x] for x in rotated_board[y]])
        for formula in formulas:
            if formula in sx:
                #  if match found, replace the first item with multiplication or division sign
                board[sx.find(formula)][y] = random.randint(0, 1)

            elif formula in sy:
                # the same, but horizontally
                board[y][sy.find(formula)] = random.randint(0, 1)

    return board


def terminate():
    pygame.quit()
    sys.exit()


def description():
    gui.clear()
    gui.add_element(info)
    gui.add_element(back)

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            gui.get_event(event)

        if back.pressed:
            main()

        gui.render(screen)
        pygame.display.flip()


def game():
    gui.clear()
    gui.add_element(back)
    try_again.pressed = False
    board.timer = 31
    board.clock = pygame.time.Clock()  # clock should be initialized at this moment, not in Bejeweled __init__

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board.get_click(event.pos)
            gui.get_event(event)

        if back.pressed:
            main()

        gui.render(screen)
        board.mainloop()
        pygame.display.flip()


def game_over():
    gui.add_element(fail)
    gui.add_element(try_again)
    gui.add_element(exit)
    if lang == 'eng':
        gui.add_element(Label((100, 200, 200, 50), 'Your Score: %d' % board.score, background_color=-1, x=500, y=250))
    elif lang == 'rus':
        gui.add_element(Label((100, 200, 200, 50), 'Ваш счет: %d' % board.score, background_color=-1, x=500, y=250))

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            gui.get_event(event)

        if try_again.pressed:
            game()
        elif exit.pressed:
            terminate()
        elif back.pressed:
            main()

        gui.render(screen)
        pygame.display.flip()


def main():
    global logo, play, rules, exit, back, fail, try_again, info
    while True:
        if lang.pressed:
            logo = Label((100, 100, 1000, 750), 'Запоминай с Physjeweled!', background_color=pygame.Color('white'),
                         font_size=70, x=290, y=250)
            play = Button((520, 450, 140, 50), 'Играть', background_color=pygame.Color('lightblue'))
            rules = Button((520, 520, 140, 50), 'Правила', background_color=pygame.Color('lightblue'))
            exit = Button((520, 590, 140, 50), 'Выход', background_color=pygame.Color('lightblue'))
            back = Button((20, 875, 110, 50), 'Назад', background_color=pygame.Color('lightblue'))
            fail = Label((100, 100, 1000, 750), 'Игра окончена', background_color=pygame.Color('white'), font_size=100,
                         x=345, y=150)
            try_again = Button((440, 450, 315, 50), 'Попробовать снова', background_color=pygame.Color('lightblue'))
            info = Label((100, 100, 1000, 750),
                         '    Physjeweled - это игра в жанре "три в ряд" для запоминания физических формул. '
                         'Используйте латинские и греческие буквы, а также знаки математических действий, '
                         'чтобы составлять формулы и получать очки!\n    '
                         'Каждая формула дает (10 * длину формулы) очков и добавляет 5 секунд к оставшемуся времени, '
                         'а каждое перемещение, начиная со второго, отнимает все больше очков. \n    '
                         'Наслаждайтесь игрой!',
                         background_color=pygame.Color('white'), font_size=70)

            gui.clear()
            gui.add_element(logo)
            gui.add_element(play)
            gui.add_element(rules)
            gui.add_element(exit)

        else:
            logo = Label((100, 100, 1000, 750), 'Memorize with Physjeweled!', background_color=pygame.Color('white'),
                         font_size=70, x=280, y=250)
            play = Button((550, 450, 100, 50), 'Play', background_color=pygame.Color('lightblue'))
            rules = Button((550, 520, 100, 50), 'Rules', background_color=pygame.Color('lightblue'))
            exit = Button((550, 590, 100, 50), 'Exit', background_color=pygame.Color('lightblue'))
            back = Button((20, 875, 100, 50), 'Back', background_color=pygame.Color('lightblue'))
            fail = Label((100, 100, 1000, 750), 'Game Over', background_color=pygame.Color('white'), font_size=100,
                         x=410,
                         y=150)
            try_again = Button((525, 450, 150, 50), 'Try Again', background_color=pygame.Color('lightblue'))
            info = Label((100, 100, 1000, 750),
                         '    Physjeweled is a Bejeweled-like game for memorizing physics formulas. '
                         'Do you have problems with remembering a particular formula from your physics course? '
                         'Use latin and greek letters and math signs and build a formula to improve your score! '
                         '\n    Each formula gives you (10 * its length) points '
                         'and 5 seconds of additional time, while each swipe, starting from the second, '
                         'takes off more and more points. \n    Enjoy!',
                         background_color=pygame.Color('white'), font_size=70)

            gui.clear()
            gui.add_element(logo)
            gui.add_element(play)
            gui.add_element(rules)
            gui.add_element(exit)

        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lang.get_event(event)
            gui.get_event(event)

        if play.pressed:
            play.pressed = False
            game()
        elif rules.pressed:
            rules.pressed = False
            description()
        elif exit.pressed:
            exit.pressed = False
            terminate()

        gui.render(screen)
        gui.update()
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()


board = Bejeweled(12, 12)
board.board = pre_check_matches(board.board)

all_sprites = pygame.sprite.Group()
AnimatedSprite(all_sprites, width // 2 + 175, height // 2 - 160)
lang = LangButton(all_sprites, 1050, 10)
gui = GUI()

if __name__ == "__main__":
    main()
