import pygame
import os


width = 600
height = 510
fps = 15
GRAVITY = 15
coords = [300, 300]
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
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'ground': load_image('ground0.png', -1),
               'sprikes': load_image('sprikes.png', -1),
               'star': load_image('star.png', -1),
               'gun_l': load_image('gun_l.png', -1),
               'gun_r': load_image('gun_r.png', -1),
               'lava': load_image('lava.png', -1)}
player_image = {'run_r': load_image('run_r.png', -1), 'run_l': load_image('run_l.png', -1),
                'shoot_l': load_image('shoot_l.png', -1), 'shoot_r': load_image('shoot_r.png', -1),
                'die': load_image('die.png', -1), 'stay': load_image('stay.png', -1)}
tile_width = 30
tile_height = 30
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullets = pygame.sprite.Group()
lava = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.frames = []
        self.cut_sheet(player_image['stay'], 1, 1)
        self.cur_frame = 0
        self.k = 0
        self.h = 0
        self.time = 0
        self.shoot = False
        self.stay = False
        self.jump = False
        self.die = False
        self.force = 11
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(coords[0], coords[1], sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        for j in pygame.sprite.spritecollide(self, tiles_group, False):
            if j.tile_type == 'sprikes':
                self.die = True
            elif j.tile_type == 'lava':
                self.die = True
        for _ in range(15):
            if len(pygame.sprite.spritecollide(self, tiles_group, False)) == 0:
                self.stay = False
                coords[1] += 1
                self.rect.y += 1
            else:
                self.stay = True
                break

        if i.type == pygame.KEYDOWN and self.die is False and self.stay is True:
            if i.key == pygame.K_SPACE:
                self.jump = True
        if i.type == pygame.KEYDOWN and self.die is False and (pygame.time.get_ticks() // 1000 - self.time) >= 2:
            if i.key == pygame.K_z:
                self.shoot = True
                self.time = pygame.time.get_ticks() // 1000
                if motion == 'right' or motion == 'stop':
                    Bullet('gun_r', coords[0] + 5, coords[1] + 5)
                    self.frames = []
                    self.cut_sheet(player_image['shoot_r'], 6, 1)
                elif motion == 'left':
                    Bullet('gun_l', coords[0] - 5, coords[1] - 5)
                    self.frames = []
                    self.cut_sheet(player_image['shoot_l'], 6, 1)

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
                self.force -= 1
                for _ in range((self.force ** 2) // 2):
                    self.rect.y -= 1
                    coords[1] -= 1
                    if len(pygame.sprite.spritecollide(self, tiles_group, False)) != 0:
                        for sp in pygame.sprite.spritecollide(self, tiles_group, False):
                            if sp.tile_type == 'ground':
                                self.rect.y += 1
                                coords[1] += 1
                                self.jump = False
                                self.force = 12
                        break
            else:
                self.jump = False
                self.force = 11

        if motion == 'left':
            coords[0] -= 6
            self.rect.x -= 6
        elif motion == 'right':
            coords[0] += 6
            self.rect.x += 6

        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        if self.shoot is True:
            self.h += 1

        if self.h == 6:
            self.h = 0
            self.shoot = False
            if motion == 'right':
                self.frames = []
                self.cut_sheet(player_image['run_r'], 7, 1)
            elif motion == 'left':
                self.frames = []
                self.cut_sheet(player_image['run_l'], 7, 1)
            elif motion == 'stop':
                self.frames = []
                self.cut_sheet(player_image['stay'], 1, 1)

        if self.die is True:
            self.k += 1
            self.frames = []
            self.cut_sheet(player_image['die'], 5, 1)
        if self.k > 0:
            self.k += 1
        if self.k == 6:
            exit()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Lava(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(lava, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(bullets)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        if self.tile_type == 'gun_r':
            self.rect.x += 50
        elif self.tile_type == 'gun_l':
            self.rect.x -= 50


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
            elif level[y][x] == '%':
                Lava('lava', x, y)
            elif level[y][x] == '!':
                Tile('star', x, y)
            elif level[y][x] == '$':
                coords = [x * 30, 390]
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
    for sprite in all_sprites:
        if sprite.tile_type != 'lava':
            sprite.rect.x -= 2
    for sprite in player_group:
        sprite.rect.x -= 2
        coords[0] -= 2
    screen.blit(fon, (0, 0))
    all_sprites.draw(screen)
    bullets.draw(screen)
    lava.draw(screen)
    bullets.update()
    player_group.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
