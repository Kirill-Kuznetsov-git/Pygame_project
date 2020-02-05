import pygame
import os


width = 700
height = 500
fps = 15
GRAVITY = 15
coords = [0, 0]
motion = 'stop'
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))
screen_rect = (0, 0, width, height)


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'ground': load_image('ground.png', -1),
               'sprikes': load_image('sprikes.png', -1),
               'star': load_image('star.png', -1)}
player_image = {'run_r': load_image('run_r.png', -1), 'run_l': load_image('run_l.png', -1),
                'jump_r': load_image('jump_r.png', -1), 'jump_l': load_image('jump_l.png', -1),
                'shoot': load_image('shoot.png', -1), 'die': load_image('die.png', -1),
                'stay': load_image('stay.png', -1)}
tile_width = 30
tile_height = 30
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.frames = []
        self.cut_sheet(player_image['stay'], 1, 1)
        self.cur_frame = 0
        self.stay = False
        self.jump = False
        self.force = 400
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(tile_width * pos_x + 15, tile_height * pos_y + 5)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(coords[0], coords[1], sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        for j in pygame.sprite.spritecollide(self, tiles_group, False):
            if j.tile_type == 'ground':
                self.stay = True
            elif j.tile_type == 'sprikes':
                pass
        if len(pygame.sprite.spritecollide(self, tiles_group, False)) == 0:
                self.stay = False
        if self.stay is False:
            coords[1] += GRAVITY

        if i.type == pygame.KEYDOWN:
            if i.key == pygame.K_SPACE and self.stay is True:
                self.jump = True
                if motion == 'right' or motion == 'stay':
                    self.cut_sheet(player_image['jump_r'], 5, 1)
                elif motion == 'left':
                    self.cut_sheet(player_image['jump_l'], 5, 1)
            if i.key == pygame.K_LEFT:
                self.frames = []
                self.cut_sheet(player_image['run_l'], 7, 1)
            elif i.key == pygame.K_RIGHT:
                self.frames = []
                self.cut_sheet(player_image['run_r'], 7, 1)
        else:
            self.frames = []
            self.cut_sheet(player_image['stay'], 1, 1)

        if self.jump is True:
            if self.force > 0:
                self.force -= 100
                self.rect.y -= 30
                coords[1] -= 30
            else:
                self.jump = False
                self.force = 400
                if motion == 'left':
                    self.frames = []
                    self.cut_sheet(player_image['run_l'], 7, 1)
                elif motion == 'right':
                    self.frames = []
                    self.cut_sheet(player_image['run_r'], 7, 1)
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

        if motion == 'stop':
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif motion == 'left':
            coords[0] -= 5
            self.rect.x -= 5
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        elif motion == 'right':
            coords[0] += 5
            self.rect.x += 5
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


def generate_level(level):
    global coords
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '@':
                Tile('ground', x, y)
            elif level[y][x] == '#':
                Tile('sprikes', x, y)
            elif level[y][x] == '!':
                Tile('star', x, y)
            elif level[y][x] == '$':
                coords = [y, x]
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


running = True
player, level_x, level_y = generate_level(load_level('level_1.txt'))
fon = pygame.transform.scale(load_image('fon.png'), (width, height))
screen.blit(fon, (0, 0))
while running:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        elif i.type == pygame.KEYDOWN:
            if i.key == pygame.K_LEFT:
                motion = 'left'
            elif i.key == pygame.K_RIGHT:
                motion = 'right'
        elif i.type == pygame.KEYUP:
            if i.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                motion = 'stop'
    screen.blit(fon, (0, 0))
    # изменяем ракурс камеры
    # обновляем положение всех спрайтов
    for sprite in all_sprites:
        sprite.rect.x -= 3
    player_group.update()
    all_sprites.draw(screen)
    player_group.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
