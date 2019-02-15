import os
import sys
import pygame
from random import randint, choice

pygame.init()
pygame.display.set_caption('Pacman')

#const
FPS = 60
WIDTH = 1200
HEIGHT = 720

# Таймеры
CHANGE = 30
CONTINUEMOVE = 31

GHOSTS = [('Inky.png', 'INKY', (26, 175, 230)),
          ('Blinky.png', 'Blinky', (231, 0, 10)),
          ('Pinky.png', 'Pinky', (242, 159, 183)),
          ('Clyde.png', 'Clyde', (231, 141, 0))]
GHOSTSGAME = [('blinky_up.png', 'blinky_down.png',
               'blinky_left.png', 'blinky_right.png'),
              ('pinky_up.png', 'pinky_down.png',
               'pinky_left.png', 'pinky_right.png'),
              ('clyde_up.png', 'clyde_down.png',
               'clyde_left.png', 'clyde_right.png'),
              ('inky_up.png', 'inky_down.png',
               'inky_left.png', 'inky_right.png')]
INTRO = [["Начать игру", 0],
         ["Управление", 0],
         ["Об игре", 0],
         ["Таблица рекордов", 0],
         ["Выход", 0]]

FULLNAME = os.path.join('data', 'Firenight-Regular.otf')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(pygame.Color("black"))

all_sprites = pygame.sprite.Group()
all_ghosts = pygame.sprite.Group()

all_maps = pygame.sprite.Group()
all_points = pygame.sprite.Group()
all_rects = pygame.sprite.Group()

ghost_sprites = pygame.sprite.Group()
pacman_kill = pygame.sprite.Group()
pacman_sprite = pygame.sprite.Group()

pygame.mouse.set_visible(False)
clock = pygame.time.Clock()


def load_image(name):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


class Ghost(pygame.sprite.Sprite):
    def __init__(self, group, ghost_name):
        super().__init__(group)
        file_name = ghost_name[0]
        text = ghost_name[1]
        self.group = group
        image = load_image(file_name)
        self.v = 5
        self.moving = True
        self.show_name = False
        self.is_moving = True
        self.made_stop = False
        self.size = image.get_width()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = - 600
        self.rect.y = HEIGHT // 2 - 180

        font = pygame.font.Font(FULLNAME, 30)
        self.text = font.render(text, 1, (ghost_name[2]))
        self.start_x = WIDTH // 2 - self.text.get_width() // 2
        self.start_y = HEIGHT // 2 - 180

    def move(self):
        if self.is_moving and self.moving:
            self.rect.x += self.v
        if not self.made_stop:
            if self.rect.x >= WIDTH // 2 + self.text.get_width() // 2 + 10:
                self.show_name = True
                self.is_moving = False
                self.made_stop = True
                pygame.time.set_timer(CONTINUEMOVE, 1000)
        if self.rect.x >= WIDTH + self.size:
            self.is_moving = False
            self.stop(1)

    def stop(self, pos=0):
        global ghost_on_screen
        if pos == 1 and self.moving:
            self.moving = False
            self.kill()
            ghost_on_screen += 1
            if ghost_on_screen == 4:
                ghost_on_screen = 0
            Ghost(all_ghosts, GHOSTS[ghost_on_screen])
            Ghost.moving = True
            Ghost.is_moving = True
            Ghost.made_stop = False

    def continue_moving(self):
        if self.moving:
            self.show_name = False
            self.is_moving = True


class StartScreen:
    def __init__(self):
        global all_sprites, INTRO
        # Скорость передвижения призрака
        self.v = 6
        # Загрузка изображения названия игры и расположение на экране
        image = load_image('start_screen.png')
        sprite = pygame.sprite.Sprite()
        sprite.image = image
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = WIDTH // 2 - image.get_width() // 2
        sprite.rect.y = 0
        all_sprites.add(sprite)

    def print_text(self):
        for i in range(len(INTRO)):
            if INTRO[i][1] == 0:
                color = pygame.Color("white")
            else:
                color = pygame.Color("yellow")
            font = pygame.font.Font(FULLNAME, 50)
            text = font.render(INTRO[i][0], 1, (color))
            start_x = WIDTH // 2 - text.get_width() // 2
            start_y = HEIGHT // 2 - text.get_height() // 2 - 50
            text_x = start_x
            text_y = start_y + i * 60
            screen.blit(text, (text_x, text_y))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen_on():
    global mouse_on_screen, music_on
    while True:
        show_start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if pygame.key.get_pressed()[pygame.K_e]:
                if music_on:
                    pygame.mixer.music.pause()
                    music_on = False
                else:
                    pygame.mixer.music.unpause()
                    music_on = True

            elif event.type == pygame.MOUSEMOTION:
                change_text_start(event.pos)
                if pygame.mouse.get_focused():
                    change_place(event.pos)
                    mouse_on_screen = event.pos
            elif event.type == CONTINUEMOVE:
                for ghost in all_ghosts:
                    ghost.continue_moving()
                pygame.time.set_timer(CONTINUEMOVE, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                if f1:
                    return
                elif f2:
                    controls_screen()
                    return
                elif f3:
                    about()
                elif f4:
                    record_menu()
                elif f5:
                    terminate()
        pygame.display.flip()


def show_start_screen():
    global mouse_on_screen
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    StartScreen.print_text(start)
    for ghost in all_ghosts:
        ghost.move()
        if ghost.show_name == 1:
            screen.blit(ghost.text, (ghost.start_x, ghost.start_y))
    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)
    all_ghosts.update()
    all_ghosts.draw(screen)


class GhostPlay(pygame.sprite.Sprite):
    def __init__(self, num):
        super().__init__(ghost_sprites)
        image = load_image(GHOSTSGAME[num % 4][0])
        size_h = image.get_height()
        self.num = num % 4
        self.v = 3
        self.way = 1
        self.p = 1
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        if num % 2 == 0:
            self.rect.x = WIDTH // 2 + 235
            self.rect.y = HEIGHT // 2 - size_h // 2 - 20
        else:
            self.rect.x = WIDTH // 2 - 272
            self.rect.y = HEIGHT // 2 - size_h // 2 - 20

    def move(self):
        global stop_game
        if self.way == 1:
            self.image = load_image(GHOSTSGAME[self.num][0])
            self.rect.y -= self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y += 2 * self.v
                self.way = choice([2, 4])

        elif self.way == 2:
            self.image = load_image(GHOSTSGAME[self.num][3])
            self.rect.x += self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x -= 2 * self.v
                self.way = choice([1, 3])

        elif self.way == 3:
            self.image = load_image(GHOSTSGAME[self.num][1])
            self.rect.y += self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y -= 2 * self.v
                self.way = choice([2, 4])

        elif self.way == 4:
            self.image = load_image(GHOSTSGAME[self.num][2])
            self.rect.x -= self.v
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x += 2 * self.v
                self.way = choice([1, 3])

        if self.way > 4:
            self.way = 1

        for pacman in pacman_sprite:
            if pygame.sprite.collide_mask(self, pacman):
                stop_game = True

    def change(self):
        last = self.way
        while self.way == 4 - last:
            self.way = randint(1, 4)


class Pacman(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(pacman_sprite)
        self.sheet_right = sheet
        self.columns, self.rows = columns, rows
        self.frames = []
        self.cut_sheet(self.sheet_right, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        if map_on_screen_num != 3:
            self.rect.x = WIDTH // 2 - 13
            self.rect.y = HEIGHT // 2 - 35
        else:
            self.rect.x = WIDTH // 2 - 7
            self.rect.y = HEIGHT // 2 - 15
        self.x1, self.y1 = self.rect.x, self.rect.y
        self.speed = 9
        self.last_pos = "right"

        self.sheet_left = pygame.transform.flip(sheet, True, False)
        self.sheet_up = pygame.transform.rotate(sheet, 90)
        self.sheet_down = pygame.transform.rotate(sheet, -90)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def move(self, pos):
        global stop_game, score
        if pos == "right":
            if self.last_pos:
                if self.last_pos == "up" or self.last_pos == "down":
                    self.rows, self.columns = self.columns, self.rows

            self.frames = []
            self.cut_sheet(self.sheet_right, self.columns, self.rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.x += self.speed
            self.x1 = self.rect.x
            self.last_pos = "right"

            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x -= self.speed
                self.x1 = self.rect.x

        if pos == "left":
            if self.last_pos:
                if self.last_pos == "up" or self.last_pos == "down":
                    self.rows, self.columns = self.columns, self.rows
            self.frames = []
            self.cut_sheet(self.sheet_left, self.columns, self.rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.x -= self.speed
            self.x1 = self.rect.x
            self.last_pos = "left"
            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.x += self.speed
                self.x1 = self.rect.x

        if pos == "up":
            if self.last_pos:
                if self.last_pos != "up" and self.last_pos != "down":
                    self.rows, self.columns = self.columns, self.rows

            self.frames = []
            self.cut_sheet(self.sheet_up, self.columns, self.rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.y -= self.speed
            self.y1 = self.rect.y
            self.last_pos = "up"

            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y += self.speed
                self.y1 = self.rect.y

        if pos == "down":
            if self.last_pos:
                if self.last_pos != "up" and self.last_pos != "down":
                    self.rows, self.columns = self.columns, self.rows

            self.frames = []
            self.cut_sheet(self.sheet_down, self.columns, self.rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(self.x1, self.y1)

            self.rect.y += self.speed
            self.y1 = self.rect.y
            self.last_pos = "down"

            if pygame.sprite.collide_mask(self, map_on_screen):
                self.rect.y -= self.speed
                self.y1 = self.rect.y

        for ghost in ghost_sprites:
            if pygame.sprite.collide_mask(self, ghost):
                if self.last_pos == "down":
                    self.rect.y -= self.speed
                if self.last_pos == "up":
                    self.rect.y += self.speed
                if self.last_pos == "left":
                    self.rect.x += self.speed
                if self.last_pos == "right":
                    self.rect.x -= self.speed
                stop_game = True

        for point in all_points:
            if pygame.sprite.collide_mask(self, point):
                f = True
                for rect in all_rects:
                    if pygame.sprite.collide_mask(self, rect):
                        f = False
                if f:
                    score += 10
                    Rects(self.rect, self.last_pos)


class Rects(pygame.sprite.Sprite):
    def __init__(self, pos, way):
        super().__init__(all_rects)
        image = load_image('rect.png')
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]

        if way == "left":
            self.image = pygame.transform.rotate(image, 90)

        if way == "right":
            self.image = pygame.transform.rotate(image, 90)


class Points(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_points)
        if map_on_screen_num == 3:
            image = load_image('points_level3.png')
        else:
            image = load_image('points.png')
        size_w = image.get_width()
        size_h = image.get_height()
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2 - size_w // 2
        self.rect.y = HEIGHT // 2 - size_h // 2


class KillPacman(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, start_x, start_y):
        super().__init__(pacman_kill)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.rect.x = start_x
        self.rect.y = start_y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]




def new_record():
    global mouse_on_screen
    name = '|'
    color_ok = None
    recorded = False
    while True:
        show_record()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and len(name) <= 8:
                if 97 <= event.key <= 122:
                    name = name[:-1] + chr(event.key).upper() + '|'
                elif event.key == 8:
                    name = name[:-2] + '|'
            elif event.type == pygame.MOUSEMOTION:
                show_record()
                if 552 <= event.pos[0] <= 608 and 395 <= event.pos[1] <= 440:
                    color_ok = pygame.Color("yellow")
                else:
                    color_ok = pygame.Color("white")
                if pygame.mouse.get_focused():
                    change_place(event.pos)
                    mouse_on_screen = event.pos

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                    event.button == 1:
                if 552 <= event.pos[0] <= 608 and 395 <= event.pos[1] <= 440:
                    player_name = name[:len(name) - 1]
                    name = 'RECORDED!'
                    recorded = True

        font = pygame.font.Font(FULLNAME, 50)
        string_rendered = font.render('Введите свое имя:', 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(410, 225)
        screen.blit(string_rendered, intro_rect)

        if color_ok:
            string_rendered = font.render('OK', 1, color_ok)
        else:
            string_rendered = font.render('OK', 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect().move(WIDTH // 2 - 30, 400)
        screen.blit(string_rendered, intro_rect)

        string_rendered = font.render(name, 1, (0, 175, 240))
        intro_rect = string_rendered.get_rect().move(495, 315)
        screen.blit(string_rendered, intro_rect)

        pygame.display.flip()
        clock.tick(FPS)
        if recorded:
            pygame.time.delay(2000)
            return player_name


def show_record():
    global mouse_on_screen
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 175, 240),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]), 10)
    pygame.draw.rect(screen, pygame.Color("black"),
                     ([WIDTH // 2 - 310, HEIGHT // 2 - 200],
                      [600, 400]))

    if mouse_on_screen and pygame.mouse.get_focused():
        change_place(mouse_on_screen)


