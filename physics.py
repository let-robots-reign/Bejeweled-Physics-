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
           12: 'data/symbol12.png', 13: 'data/symbol13.png', 14: 'data/symbol14.png', 15: 'data/symbol15.png',
           16: 'data/symbol16.png', 17: 'data/symbol17.png'}  # convert board values to images

numbers_to_letters = {-1: 'X', 0: '*', 1: '/', 2: 'F', 3: 'm', 4: 'g', 5: 'I', 6: 'U', 7: 'S', 8: 't', 9: 'v', 10: 'a',
                      11: 'V', 12: 'p', 13: 'h', 14: 'N', 15: 'R', 16: 'q', 17: 'A'}  # convert board values to letters

formulas = {'m*g': 'F', 'U/I': 'R', 'U/R': 'I', 'I*R': 'U', 'q/t':'I', 'I*t':'q', 'q/I':'t', 'A/q':'U', 'U*q':'A',
            'A/U': 'q', 'A/t': 'N', 'S/v': 't', 'S/t': 'v', 'v*t': 'S', 'v/t': 'a', 'a*t': 'v(x)', 'g*t': 'v(y)',
            'p*V': 'm', 'm/V': 'p', 'm/p': 'V', 'm*a': 'F', 'm*v': 'p', 'q*m': 'Q', 'F/S': 'P', 'F/m': 'a', 'F/a': 'm',
            'F*t': 'p', 'F*S': 'A', 'A/F': 'S', 'A/S': 'F', 'N*t': 'A', 'A/N': 't', 'p*g*h': 'P', 'p*g*V': 'Fa',
            'm*g*h': 'Eп', 'I*U*t': 'Q'}  # formulas to be in the game


game_sounds = {'swap': pygame.mixer.Sound('data/swap.wav'), 'match': [pygame.mixer.Sound('data/match1.wav'),
              pygame.mixer.Sound('data/match2.wav'), pygame.mixer.Sound('data/match3.wav'),
              pygame.mixer.Sound('data/match4.wav'), pygame.mixer.Sound('data/match5.wav')]}
# sounds to be played after an action


class AnimatedSprite(pygame.sprite.Sprite):  # animated image of atom, displayed on menu screen
    def __init__(self, group, x, y):
        super().__init__(group)
        self.frame_index = 0
        self.image = pygame.image.load('data/atom_animation/atom0.gif')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clock = pygame.time.Clock()
        self.fps = 30

    def update(self):
        self.frame_index = (self.frame_index + 1) % 40  # 40 - number of frames
        self.image = pygame.image.load('data/atom_animation/atom%s.gif' % self.frame_index)  # updating the image
        self.clock.tick(self.fps)


class LangButton(pygame.sprite.Sprite):  # button changing the language
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.image.load('data/eng.png')  # initially it's English
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.pressed = False

    def update(self):
        if self.pressed:
            self.image = pygame.image.load('data/rus.png')
        else:
            self.image = pygame.image.load('data/eng.png')

    def get_event(self, event):
        if self.rect.collidepoint(event.pos):
            self.pressed = not self.pressed
        # change all gui items
        if self.pressed:
            eng_to_rus()
        else:
            rus_to_eng()


class Arrow(pygame.sprite.Sprite):  # custom arrow
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.image.load('data/cursor.png')
        self.rect = self.image.get_rect()

    def update(self):
        if pygame.mouse.get_focused():
            self.rect.x, self.rect.y = pygame.mouse.get_pos()


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
        self.collected = []  # list of collected formulas
        self.frequencies = {}  # dict of frequencies
        self.font = pygame.font.Font(None, 40)
        self.score_text = None
        self.timer_text = None
        self.timer = 0  # timer initializing is in game()
        self.dt = 0  # delta
        self.clock = None  # clock initializing is in game()

        for i in range(25):  # 25 multiplications
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

        self.board = self.pre_check_matches()  # check for matches

    def random_coords(self):
        return random.randint(0, self.width - 1), random.randint(0, self.height - 1)

    def get_cell(self, mouse_pos):
        cell_x = (mouse_pos[0] - self.left) // self.cell_size
        if cell_x < 0 or cell_x > self.width - 1:
            return None
        cell_y = (mouse_pos[1] - self.top) // self.cell_size
        if cell_y < 0 or cell_y > self.height - 1:
            return None
        return cell_x, cell_y

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def pre_check_matches(self):  # eliminating all matches before starting
        rotated_board = list(map(list, zip(*self.board)))
        for y in range(len(self.board)):
            sy = ''.join([numbers_to_letters[x] for x in self.board[y]])  # rows
            sx = ''.join([numbers_to_letters[x] for x in rotated_board[y]])  # columns
            for formula in formulas.keys():
                if formula in sx:
                    #  if match found, replace the first item with multiplication or division sign
                    self.board[sx.find(formula)][y] = random.randint(0, 1)

                elif formula in sy:
                    # the same, but horizontally
                    self.board[y][sy.find(formula)] = random.randint(0, 1)

        return self.board

    def shift_tiles_down(self):
        board = list(map(list, zip(*self.board)))  # zipping the board to iterate its columns
        for y in range(len(board)):
            if -1 in board[y]:
                # shifting
                board[y] = [-1] * board[y].count(-1) + board[y][:board[y].index(-1)] + \
                           board[y][board[y].index(-1) + board[y].count(-1):]
                for i in range(board[y].count(-1)):
                    board[y][i] = random.randint(0, len(symbols) - 1)  # refilling
        board = list(map(list, zip(*board)))  # zip the board back
        return board

    def mainloop(self):
        rotated_board = list(map(list, zip(*self.board)))  # zipping the board to iterate its columns
        for y in range(self.height):
            sy = ''.join([numbers_to_letters[x] for x in self.board[y]])  # rows
            sx = ''.join([numbers_to_letters[x] for x in rotated_board[y]])  # columns
            for formula in formulas.keys():  # finding vertical matches
                if formula in sx:
                    sound_index = random.randint(0, 4)
                    game_sounds['match'][sound_index].play()
                    self.collected.append(formula)
                    self.frequencies[formula] = self.frequencies.get(formula, 0) + 1
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
                    self.collected.append(formula)
                    self.frequencies[formula] = self.frequencies.get(formula, 0) + 1
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

        #  rect with collected formulas displayed
        pygame.draw.rect(screen, pygame.Color('red'), (900, 168, 250, 640), 3)
        for i in range(len(list(reversed(self.collected[-10:])))):
            screen.blit(pygame.font.Font(None, 80).render('%s = %s' % (list(reversed(self.collected[-10:]))[i],
                       formulas[list(reversed(self.collected[-10:]))[i]]), 1, pygame.Color('black')), (920, 170 + 64*i))

        # changing language during the game
        if lang.pressed:
            self.score_text = self.font.render('Счет: %d' % self.score, 1, pygame.Color('black'))
            self.timer_text = self.font.render('Время: %d' % self.timer, 1, pygame.Color('black'))
        else:
            self.score_text = self.font.render('Score: %d' % self.score, 1, pygame.Color('black'))
            self.timer_text = self.font.render('Time: %d' % self.timer, 1, pygame.Color('black'))
        screen.blit(self.score_text, (900, 55))
        screen.blit(self.timer_text, (900, 119))

        self.board = self.shift_tiles_down()  # shifting the tiles

        # time management
        if self.timer - self.dt > 0:
            self.timer -= self.dt
        else:
            self.pressed = ()  # when time's left, everything's unpressed
            game_over()

        self.dt = self.clock.tick(1000) / 1000

    def on_click(self, cell):
        if cell == self.pressed:
            self.pressed = ()  # second pressing makes the cell inactive
        else:
            if self.pressed:
                # swapping
                self.swaps += 1
                if self.score - self.swaps > 0:
                    self.score -= self.swaps
                else:
                    self.score = 0
                if abs(cell[0] - self.pressed[0]) <= 1 and abs(cell[1] - self.pressed[1]) <= 1 \
                        and (abs(cell[0] - self.pressed[0]) == 0 or abs(cell[1] - self.pressed[1]) == 0):
                    game_sounds['swap'].play()
                    self.board[self.pressed[1]][self.pressed[0]], self.board[cell[1]][cell[0]] = self.board[cell[1]][cell[0]], self.board[self.pressed[1]][self.pressed[0]]
                    self.pressed = ()  # cell is inactive
                else:
                    self.pressed = ()  # cell is inactive after swapping
            else:
                self.pressed = cell  # cell is active


def eng_to_rus():  # transferring all gui items from english to russian
    global logo, play, rules, exit, back, fail, try_again, info  # global is unwanted, but compelled here
    logo = Label((100, 100, 1000, 750), 'Запоминай с Physjeweled!', background_color=pygame.Color('white'),
                 font_size=70, x=280, y=250)
    play = Button((530, 450, 140, 50), 'Играть', background_color=pygame.Color('lightblue'))
    rules = Button((530, 520, 140, 50), 'Правила', background_color=pygame.Color('lightblue'))
    exit = Button((530, 590, 140, 50), 'Выход', background_color=pygame.Color('lightblue'))
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


def rus_to_eng():  # transferring all gui items from russian to english
    global logo, play, rules, exit, back, fail, try_again, info  # global is unwanted, but compelled here
    logo = Label((100, 100, 1000, 750), 'Memorize with Physjeweled!', background_color=pygame.Color('white'),
                 font_size=70, x=270, y=250)
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


def get_best_score():  # acquiring the best score from the file
    with open('best_score.txt', 'r') as score_list:
        return int(score_list.read().strip())


def rewrite_best_score(score):  # rewriting the best score
    with open('best_score.txt', 'w') as score_list:
        score_list.write(str(score))


def terminate():
    pygame.quit()
    sys.exit()


def description():  # 'rules' menu
    gui.clear()
    gui.add_element(info)
    gui.add_element(back)

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lang.get_event(event)
                gui.clear()
                gui.add_element(info)
                gui.add_element(back)

            gui.get_event(event)

        if back.pressed:
            back.pressed = False
            main()

        gui.render(screen)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()


def game():  # game process
    gui.clear()
    gui.add_element(back)
    board.timer = 31
    board.clock = pygame.time.Clock()  # clock should be initialized at this moment, not in Bejeweled __init__

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board.get_click(event.pos)
                lang.get_event(event)
                gui.clear()
                gui.add_element(back)

            gui.get_event(event)

        if back.pressed:
            back.pressed = False
            board.__init__(12, 12)  # new board construction
            main()

        gui.render(screen)
        board.mainloop()
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()


def game_over():  # 'game over' screen
    gui.clear()
    gui.add_element(fail)
    gui.add_element(try_again)
    gui.add_element(exit)
    best_score = get_best_score()
    if board.score > best_score:
        rewrite_best_score(board.score)
        best_score = board.score
    if lang.pressed:
        gui.add_element(Label((100, 200, 200, 50), 'Ваш счет: %d' % board.score, background_color=-1, x=500, y=250))
        gui.add_element(Label((100, 200, 200, 50), 'Лучший счет: %d' % best_score, background_color=-1,
                              x=480 - len(str(best_score)), y=315))
    else:
        gui.add_element(Label((100, 200, 200, 50), 'Your Score: %d' % board.score, background_color=-1, x=500, y=250))
        gui.add_element(Label((100, 200, 200, 50), 'Best Score: %d' % best_score, background_color=-1,
                              x=500 - len(str(best_score)), y=315))

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lang.get_event(event)
                gui.clear()
                gui.add_element(fail)
                gui.add_element(try_again)
                gui.add_element(exit)
                if lang.pressed:
                    gui.add_element(
                        Label((100, 200, 200, 50), 'Ваш счет: %d' % board.score, background_color=-1, x=500, y=250))
                    gui.add_element(Label((100, 200, 200, 50), 'Лучший счет: %d' % best_score, background_color=-1,
                                          x=480 - len(str(best_score)), y=315))
                else:
                    gui.add_element(
                        Label((100, 200, 200, 50), 'Your Score: %d' % board.score, background_color=-1, x=500, y=250))
                    gui.add_element(Label((100, 200, 200, 50), 'Best Score: %d' % best_score, background_color=-1,
                                          x=500 - len(str(best_score)), y=315))

            gui.get_event(event)

        if try_again.pressed:
            try_again.pressed = False
            board.__init__(12, 12)  # new board construction
            game()
        elif back.pressed:
            back.pressed = False
            board.__init__(12, 12)
            main()
        elif exit.pressed:
            terminate()

        gui.render(screen)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()


def main():  # main menu
    if lang.pressed:
        eng_to_rus()
    else:
        rus_to_eng()

    all_sprites.add(atom)
    gui.clear()
    gui.add_element(logo)
    gui.add_element(play)
    gui.add_element(rules)
    gui.add_element(exit)

    while True:
        screen.fill(pygame.Color('lightblue'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lang.get_event(event)
                gui.clear()
                gui.add_element(logo)
                gui.add_element(play)
                gui.add_element(rules)
                gui.add_element(exit)

            gui.get_event(event)

        if play.pressed:
            play.pressed = False
            all_sprites.remove(atom)
            game()
        elif rules.pressed:
            rules.pressed = False
            all_sprites.remove(atom)
            description()
        elif exit.pressed:
            terminate()

        gui.render(screen)
        all_sprites.draw(screen)
        all_sprites.update()
        all_sprites.move_to_front(arrow)
        pygame.display.flip()


board = Bejeweled(12, 12)

all_sprites = pygame.sprite.LayeredUpdates()
atom = AnimatedSprite(all_sprites, width // 2 + 160, height // 2 - 160)
lang = LangButton(all_sprites, 1050, 10)
arrow = Arrow(all_sprites)
gui = GUI()
pygame.mouse.set_visible(False)

if __name__ == "__main__":
    main()
