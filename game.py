import pygame
import os


width = 600
height = 510
fps = 15
GRAVITY = 21
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

    #дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'ground': load_image('ground0.png', -1),
               'sprikes': load_image('sprikes.png', -1),
               'star': load_image('star.png', -1)}
player_image = {'run_r': load_image('run_r.png', -1), 'run_l': load_image('run_l.png', -1),
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
        self.die = False
        self.force = 10
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

    def update(self, *args):
        if load_level('level_1.txt')[int(coords[1] // 30) - 1][int(coords[0] // 30)] == '@':
            print(load_level('level_1.txt')[int(coords[1] // 30) - 1][int(coords[0] // 30)])
        for j in pygame.sprite.spritecollide(self, tiles_group, False):
            if j.tile_type == 'ground':
                self.stay = True
            elif j.tile_type == 'sprikes':
                self.die = True
        if len(pygame.sprite.spritecollide(self, tiles_group, False)) == 0:
            self.stay = False

        if self.stay is False:
            coords[1] += GRAVITY
            self.rect.y += GRAVITY

        if i.type == pygame.KEYDOWN and self.die is False:
            if i.key == pygame.K_SPACE and self.stay is True:
                self.jump = True

        if args[0] is True and motion == 'left' and self.die is False:
            self.frames = []
            self.cut_sheet(player_image['run_l'], 7, 1)
        elif args[0] is True and motion == 'right' and self.die is False:
            self.frames = []
            self.cut_sheet(player_image['run_r'], 7, 1)
        elif args[0] is True and motion == 'stop' and self.die is False:
            self.frames = []
            self.cut_sheet(player_image['stay'], 1, 1)

        if self.jump is True and self.die is False:
            if self.force > 0:
                if self.force >= 0:
                    self.rect.y -= (self.force ** 2) / 2
                    coords[1] -= (self.force ** 2) / 2
                else:
                    self.rect.y += (self.force ** 2) / 2
                    coords[1] += (self.force ** 2) / 2
                self.force -= 1
            else:
                self.jump = False
                self.force = 10

        if motion == 'left':
            coords[0] -= 5
            self.rect.x -= 5
        elif motion == 'right':
            coords[0] += 5
            self.rect.x += 5
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        if self.die is True:
            self.frames = []
            self.cut_sheet(player_image['die'], 5, 1)


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
    up = False
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        elif i.type == pygame.KEYDOWN:
            if i.key == pygame.K_LEFT:
                motion = 'left'
                player_group.update(True)
                up = True
            elif i.key == pygame.K_RIGHT:
                motion = 'right'
                player_group.update(True)
                up = True
        elif i.type == pygame.KEYUP:
            if i.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                motion = 'stop'
                player_group.update(True)
                up = True
    if up is False:
        player_group.update(False)
    screen.blit(fon, (0, 0))
    for sprite in all_sprites:
        sprite.rect.x -= 1
    for sprite in player_group:
        sprite.rect.x -= 1
        coords[0] -= 1
    all_sprites.draw(screen)
    player_group.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
