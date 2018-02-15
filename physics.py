import pygame
import random
from gui import *

pygame.init()
width, height = 1200, 1000
size = width, height
screen = pygame.display.set_mode(size)
symbols = {0: 'data/symbol0.png', 1: 'data/symbol1.png', 2: 'data/symbol2.png', 3: 'data/symbol3.png',
           4: 'data/symbol4.png', 5: 'data/symbol5.png', 6: 'data/symbol6.png', 7: 'data/symbol7.png',
           8: 'data/symbol8.png', 9: 'data/symbol9.png', 10: 'data/symbol10.png', 11: 'data/symbol11.png',
           12: 'data/symbol12.png'}  # convert board values to images
numbers_to_letters = {-1: 'X', 0: '*', 1: '/', 2: 'π', 3: 'm', 4: 'g', 5: 'I', 6: 'U', 7: 'S', 8: 't', 9: 'v', 10: 'a', 11: 'V',
                      12: 'p'}  # convert board values to letters
formulas = ['m*g', 'U/I', 'S/v', 'S/t', 'v*t', 'v/t', 'a*t', 'p*V', 'm/V', 'm/p', 'm*a', 'm*v']  # formulas to be in the game
game_sounds = {'swap': pygame.mixer.Sound('data/swap.wav'), 'match': [pygame.mixer.Sound('data/match1.wav'),
              pygame.mixer.Sound('data/match2.wav'), pygame.mixer.Sound('data/match3.wav'),
              pygame.mixer.Sound('data/match4.wav'), pygame.mixer.Sound('data/match5.wav')]}  # sounds to be played after an action


def pre_check_matches(board):  # eliminating all matches before starting
    rotated_board = list(map(list, zip(*board)))
    for y in range(len(board)):
        sy = ''.join([numbers_to_letters[x] for x in board[y]])
        for x in range(len(board[y])):
            sx = ''.join([numbers_to_letters[x] for x in rotated_board[x]])
            for formula in formulas:
                if formula in sx:
                    #  if match found, replace the first item with multiplication or division sign
                    board[sx.find(formula)][x] = random.randint(0, 1)

        for formula in formulas:
            if formula in sy:
                # the same, but horizontally
                board[y][sy.find(formula)] = random.randint(0, 1)

    return board


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


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[-1 for _ in range(width)] for _ in range(height)]  # -1 is an empty cell
        self.left = 120
        self.top = 20
        self.cell_size = 64


class Bejeweled(Board):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pressed = ()  # coords of the pressed cell

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
                    board[y][i] = random.randint(0, len(symbols) - 1) # refilling
        board = list(map(list, zip(*board)))  # zip the board back
        return board

    def mainloop(self):
        rotated_board = list(map(list, zip(*self.board)))  # zipping the board to iterate its columns
        for y in range(self.height):
            sy = ''.join([numbers_to_letters[x] for x in self.board[y]])
            for x in range(self.width):
                sx = ''.join([numbers_to_letters[x] for x in rotated_board[x]])
                for formula in formulas:  # finding vertical matches
                    if formula in sx:
                        sound_index = random.randint(0, 4)
                        game_sounds['match'][sound_index].play()
                        # pygame.draw.rect(screen, pygame.Color('red'),
                        #                  (x * self.cell_size + self.left,
                        #                   sx.find(formula) * self.cell_size + self.top,
                        #                   self.cell_size, self.cell_size * len(formula)), 3)
                        for i in range(len(formula)):
                            self.board[sx.find(formula) + i][x] = -1

                if self.board[y][x] != -1:  # blitting the picture
                    img = pygame.image.load(symbols[self.board[y][x]])
                    screen.blit(img, (x * self.cell_size + self.left, y * self.cell_size + self.top))

                pygame.draw.rect(screen, pygame.Color('white'),  # drawing cells
                    (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size, self.cell_size), 1)

            for formula in formulas:  # finding horizontal matches
                if formula in sy:
                    sound_index = random.randint(0, 4)
                    game_sounds['match'][sound_index].play()
                    # pygame.draw.rect(screen, pygame.Color('red'),
                    #                  (sy.find(formula) * self.cell_size + self.left,
                    #                   y * self.cell_size + self.top,
                    #                   self.cell_size * len(formula), self.cell_size), 3)
                    for i in range(len(formula)):
                        self.board[y][sy.find(formula) + i] = -1

        if self.pressed:  # framing of the pressed cell
            pygame.draw.rect(screen, pygame.Color('red'),
                             (self.pressed[0] * self.cell_size + self.left, self.pressed[1] * self.cell_size + self.top,
                              self.cell_size, self.cell_size), 3)

        self.board = self.shift_tiles_down()  # shifting the tiles

    def on_click(self, cell):
        if cell == self.pressed:
            self.pressed = ()  # second pressing makes the cell inactive
        else:
            if self.pressed:
                # swapping
                if abs(cell[0] - self.pressed[0]) <= 1 and abs(cell[1] - self.pressed[1]) <= 1 \
                        and (abs(cell[0] - self.pressed[0]) == 0 or abs(cell[1] - self.pressed[1]) == 0):
                    game_sounds['swap'].play()
                    self.board[self.pressed[1]][self.pressed[0]], self.board[cell[1]][cell[0]] = self.board[cell[1]][cell[0]], self.board[self.pressed[1]][self.pressed[0]]
                    self.pressed = ()  # cell is inactive
                else:
                    self.pressed = ()  # cell is inactive after swapping
            else:
                self.pressed = cell  # cell is active


board = Bejeweled(12, 12)
board.board = pre_check_matches(board.board)
screen_color = pygame.Color('white')
gui = GUI()
gui.add_element(Label((300, 250, 150, 70), 'Memorize with Physjeweled!', background_color=-1))
play = Button((550, 450, 100, 50), 'Play', background_color=pygame.Color('lightblue'))
gui.add_element(play)
rules = Button((550, 520, 100, 50), 'Rules', background_color=pygame.Color('lightblue'))
gui.add_element(rules)
exit = Button((550, 590, 100, 50), 'Exit', background_color=pygame.Color('lightblue'))
gui.add_element(exit)
all_sprites = pygame.sprite.Group()
AnimatedSprite(all_sprites, width // 2 + 175, height // 2 - 175)

running = True
menu = True

while menu and running:
    screen.fill(screen_color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        gui.get_event(event)

    if play.pressed:
        menu = False
    elif rules.pressed:
        menu = False
    elif exit.pressed:
        running = False

    gui.render(screen)
    gui.update()
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()

screen_color = pygame.Color('lightblue')

while running:
    screen.fill(screen_color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            board.get_click(event.pos)

    board.mainloop()
    pygame.display.flip()

pygame.quit()