import pygame
import os
import random
import menu_start
import menu_middle


# загрузка изображений


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

# загрузка уровния с txt файла


def load_level(filename):
    filename = filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))

# переменные которые не изменяются


width = 700
height = 610
fps = 20
GRAVITY = 15


tile_width = 30
tile_height = 30
player = None

# класс главного героя


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
        self.time_pain = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.rect.x = coords[0]
        self.rect.y = coords[1]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(coords[0], coords[1], sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for k in range(columns):
                frame_location = (self.rect.w * k, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        global life
        global pain
        # проверка на прикосновение к шипам, пулям, лаве и противникам
        for j in pygame.sprite.spritecollide(self, tiles_group, False):
            if j.tile_type == 'sprikes' or j.tile_type == 'sprikes_up':
                if (pygame.time.get_ticks() // 1000 - self.time_pain) >= 2 and immortality is False:
                    if life - 1 > 0:
                        self.time_pain = pygame.time.get_ticks() // 1000
                        life -= 1
                        pain = True
                    else:
                        self.die = True
        if (len(pygame.sprite.spritecollide(self, bullets_en, False)) != 0 or
             len(pygame.sprite.spritecollide(self, enemy, False)) != 0) and (pygame.time.get_ticks() // 1000 - self.time_pain) >= 2 and immortality is False:
            if life - 1 > 0:
                self.time_pain = pygame.time.get_ticks() // 1000
                life -= 1
                pain = True
            else:
                self.die = True
        if len(pygame.sprite.spritecollide(self, lava, False)) != 0:
            self.die = True

        # реализация прыжка
        for _ in range(15):
            if len(pygame.sprite.spritecollide(self, tiles_group, False)) == 0:
                self.stay = False
                coords[1] += 1
                self.rect.y += 1
            else:
                self.stay = True
                break

        if args[2] is True and self.die is False and self.stay is True:
                self.jump = True
        # смена анимации при случаи выстрела
        if args[1] is True and self.die is False and (pygame.time.get_ticks() // 1000 - self.time) >= 1:
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

        # смена анимации при случае смены направления ходьбы
        if args[0] is True and motion == 'left' and self.die is False:
            self.frames = []
            self.cut_sheet(player_image['run_l'], 7, 1)
        elif args[0] is True and motion == 'right' and self.die is False:
            self.frames = []
            self.cut_sheet(player_image['run_r'], 7, 1)
        elif args[0] is True and motion == 'stop' and self.die is False:
            self.frames = []
            self.cut_sheet(player_image['stay'], 1, 1)
        # если во время прыжка игрок напирается на ground
        if self.jump is True and self.die is False:
            if self.force > 0:
                self.force -= 1
                for _ in range((self.force ** 2) // 2):
                    self.rect.y -= 1
                    coords[1] -= 1
                    if len(pygame.sprite.spritecollide(self, tiles_group, False)) != 0:
                        for sp in pygame.sprite.spritecollide(self, tiles_group, False):
                            if sp.tile_type == 'ground' or sp.tile_type == 'ground_l' or sp.tile_type == 'ground_r' or sp.tile_type == 'end':
                                self.rect.y += 1
                                coords[1] += 1
                                self.jump = False
                                self.force = 11
                        break
            else:
                self.jump = False
                self.force = 11
        # если во время пходьбы игрок напирается на ground
        if motion == 'left' and coords[0] < width:
            coords[0] -= 6
            self.rect.x -= 6
            for j in pygame.sprite.spritecollide(self, tiles_group, False):
                if j.tile_type == 'ground' or j.tile_type == 'ground_l' or j.tile_type == 'ground_r' or j.tile_type == 'end':
                    if j.rect.x < coords[0] and j.rect.y - coords[1] < 25:
                        coords[0] += 6
                        self.rect.x += 6
        elif motion == 'right' and coords[0] < width - 30:
            coords[0] += 6
            self.rect.x += 6
            for j in pygame.sprite.spritecollide(self, tiles_group, False):
                if j.tile_type == 'ground' or j.tile_type == 'ground_l' or j.tile_type == 'ground_r' or j.tile_type == 'end':
                    if j.rect.x > coords[0] and j.rect.y - coords[1] < 25:
                        coords[0] -= 6
                        self.rect.x -= 6
                elif j.tile_type == 'door' and key is True:
                    pygame.quit()
                    menu_middle.start()
                elif j.tile_type == 'door' and key is False:
                    coords[0] -= 6
                    self.rect.x -= 6
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        # подсчет количества пуль на карте
        if self.shoot is True:
            self.h += 1
        # сменя анимации на ходьбу после окончания выстрела
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
        # анимация смерти героя
        if self.die is True:
            self.k += 1
            self.frames = []
            self.cut_sheet(player_image['die'], 5, 1)
        if self.k > 0:
            self.k += 1
        if self.k == 6:
            pygame.mixer.music.pause()
            pygame.mixer.music.load('die.mp3')
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.5)
            pygame.time.delay(5000)
            pygame.quit()
            menu_start.start()

# класс где находятся все tiles


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

# отдельный класс для лавы


class Lava(pygame.sprite.Sprite):
    def __init__(self, tile_type,  pos_x, pos_y):
        super().__init__(lava)
        self.frames = []
        self.coords = [tile_width * pos_x, tile_height * pos_y]
        self.cut_sheet(tile_images[tile_type], 7, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x - 10, tile_height * pos_y - 10)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.coords[0] - 10, self.coords[1] - 10, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

# отдельный класс пуль


class Bullet(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(bullets)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        # пуля умирает, если соприкасается с землей
        if len(pygame.sprite.spritecollide(self, tiles_group, False)) != 0:
            for i in pygame.sprite.spritecollide(self, tiles_group, False):
                if i.tile_type == 'ground' or i.tile_type == 'ground_l' or i.tile_type == 'ground_r' or i.tile_type == 'end':
                    self.kill()
        if self.tile_type == 'gun_r':
            self.rect.x += 20
        elif self.tile_type == 'gun_l':
            self.rect.x -= 20
        # пуля умирает, если уходит на края экрана
        if self.rect.x >= width:
            self.kill()

# отдельный класс для пуль противника


class Bullet_en(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(bullets_en)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(pos_x, pos_y)

    def update(self):
        if len(pygame.sprite.spritecollide(self, tiles_group, False)) != 0:
            for i in pygame.sprite.spritecollide(self, tiles_group, False):
                if i.tile_type == 'ground' or i.tile_type == 'ground_l' or i.tile_type == 'ground_r' or i.tile_type == 'end':
                    self.kill()
        if self.tile_type == 'en_gun_r':
            self.rect.x += 15
        elif self.tile_type == 'en_gun_l':
            self.rect.x -= 15

# класс для жизней


class Live(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(hearts)
        self.image = tile_images['heart']
        self.tile_type = 'heart'
        self.rect = self.image.get_rect().move(pos_x, pos_y)

# класс для обозначения бессмертия


class Potion_mark(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(potion_mark)
        self.image = tile_images['potion']
        self.tile_type = 'potion'
        self.rect = self.image.get_rect().move(pos_x, pos_y)

# класс  зельев


class Potion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, potion)
        self.image = tile_images['potion']
        self.tile_type = 'potion'
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        global immortality
        global time_imorlat
        if len(pygame.sprite.spritecollide(self, player_group, False)) != 0:
            immortality = True
            Potion_mark(500, 50)
            self.kill()
            time_imorlat = pygame.time.get_ticks() // 1000
        if pygame.time.get_ticks() // 1000 - time_imorlat >= 5 and immortality is True:
            potion_mark.empty()
            immortality = False

# отдельный класс для ключа


class Key(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, key_group, all_sprites)
        self.image = tile_images[tile_type]
        self.tile_type = tile_type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

    def update(self):
        global key
        if len(pygame.sprite.spritecollide(self, player_group, False)) != 0:
            self.kill()
            key = True

# класс противников


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy)
        self.frames = []
        self.coords = [tile_width * pos_x + 15, tile_height * pos_y + 5]
        if random.choice([1, 2]) == 1:
            self.cut_sheet(enemy_image['en_stay_l'], 1, 1)
            self.motion = 'left'
        else:
            self.cut_sheet(enemy_image['en_stay_r'], 1, 1)
            self.motion = 'right'
        self.cur_frame = 0
        self.k = 0
        self.h = 0
        self.time = 0
        self.time_s = 0
        self.shoot = False
        self.die = False
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(tile_width * pos_x + 15, tile_height * pos_y + 5)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(self.coords[0], self.coords[1], sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        if len(pygame.sprite.spritecollide(self, bullets, False)) != 0:
            self.die = True
            bullets.empty()
        elif len(pygame.sprite.spritecollide(self, lava, False)) != 0:
            self.die = True
            bullets.empty()
        self.rect.x -= 3
        self.coords[0] -= 3
        if self.shoot is True:
            self.h += 1
        if self.h == 5:
            self.h = 0
            self.shoot = False
            if self.motion == 'left':
                self.frames = []
                self.cut_sheet(enemy_image['en_stay_l'], 1, 1)
            elif self.motion == 'right':
                self.frames = []
                self.cut_sheet(enemy_image['en_stay_r'], 1, 1)

        if (pygame.time.get_ticks() // 1000 - self.time) >= 1:
            self.time = pygame.time.get_ticks() // 1000
            if self.motion == 'left':
                self.motion = 'right'
                self.frames = []
                self.cut_sheet(enemy_image['en_stay_r'], 1, 1)
            else:
                self.motion = 'left'
                self.frames = []
                self.cut_sheet(enemy_image['en_stay_l'], 1, 1)

        if self.motion == 'left' and self.h == 0 and (pygame.time.get_ticks() // 1000 - self.time_s) >= 2:
            if self.coords[0] - 300 < coords[0] < self.coords[0] and self.coords[1] - 5 < coords[1] < self.coords[1] + 5:
                self.time_s = pygame.time.get_ticks() // 1000
                self.frames = []
                self.cut_sheet(enemy_image['en_shoot_l'], 5, 1)
                Bullet_en('en_gun_l', self.coords[0] - 5, self.coords[1])
                self.shoot = True
        elif self.motion == 'right' and self.h == 0 and (pygame.time.get_ticks() // 1000 - self.time_s) >= 2:
            if self.coords[0] < coords[0] < self.coords[0] + 300 and self.coords[1] - 5 < coords[1] < self.coords[1] + 5:
                self.time_s = pygame.time.get_ticks() // 1000
                self.frames = []
                self.cut_sheet(enemy_image['en_shoot_r'], 5, 1)
                Bullet_en('en_gun_r', self.coords[0] + 5, self.coords[1])
                self.shoot = True

        if self.die is True:
            self.k += 1
            self.frames = []
            if self.motion == 'right':
                self.cut_sheet(enemy_image['en_die_r'], 5, 1)
            elif self.motion == 'left':
                self.cut_sheet(enemy_image['en_die_l'], 5, 1)
        if self.k > 0:
            self.k += 1
        if self.k == 6:
            self.kill()

        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

# генерирование уровней


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
            elif level[y][x] == '&':
                Enemy(x, y)
            elif level[y][x] == '<':
                Tile('ground_l', x, y)
            elif level[y][x] == '>':
                Tile('ground_r', x, y)
            elif level[y][x] == '-':
                Potion(x, y)
            elif level[y][x] == '^':
                Tile('end', x, y)
            elif level[y][x] == '!':
                Key('key', x, y)
            elif level[y][x] == '1':
                Tile('start', x, y)
            elif level[y][x] == '?':
                Tile('door', x, y)
            elif level[y][x] == '$':
                coords = [(x + 2) * 30, 300]
                new_player = Player(x + 2, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y

# функция, в которой находится главный цикл. функция нужна для взаимодействия с меню


def main(level):
    global tile_images
    global player_image
    global enemy_image
    global motion
    global all_sprites
    global tiles_group
    global player_group
    global bullets
    global bullets_en
    global lava
    global enemy
    global coords
    global en_motion
    global key
    global life
    global pain
    global hearts
    global potion_mark
    global key_group
    global potion
    global immortality
    global time_imorlat
    key = False
    immortality = False
    life = 3
    time_imorlat = 0
    pain = False
    coords = [350, 300]
    motion = 'stop'
    en_motion = 'left'
    screen = pygame.display.set_mode((width, height))
    screen_rect = (0, 0, width, height)
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    tile_images = {'ground': load_image('ground.png', -1),
                   'ground_r': load_image('ground_r.png', -1),
                   'ground_l': load_image('ground_l.png', -1),
                   'sprikes': load_image('sprikes.png', -1),
                   'end': load_image('end.png', -1),
                   'key': load_image('key.png', -1),
                   'gun_l': load_image('gun_l.png', -1),
                   'gun_r': load_image('gun_r.png', -1),
                   'lava': load_image('lava.png', -1),
                   'en_gun_l': load_image('en_gun_l.png', -1),
                   'en_gun_r': load_image('en_gun_r.png', -1),
                   'door': load_image('door.png', -1),
                   'start': load_image('start.png', -1),
                   'heart': load_image('heart.png', -1),
                   'potion': load_image('potion.png', -1)
                   }
    player_image = {'run_r': load_image('run_r.png', -1), 'run_l': load_image('run_l.png', -1),
                    'shoot_l': load_image('shoot_l.png', -1), 'shoot_r': load_image('shoot_r.png', -1),
                    'die': load_image('die.png', -1), 'stay': load_image('stay.png', -1)}
    enemy_image = {'en_shoot_l': load_image('en_shoot_l.png', -1), 'en_shoot_r': load_image('en_shoot_r.png', -1),
                   'en_die_l': load_image('en_die_l.png', -1), 'en_die_r': load_image('en_die_r.png', -1),
                   'en_stay_r': load_image('en_stay_r.png', -1), 'en_stay_l': load_image('en_stay_l.png', -1)}

    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bullets_en = pygame.sprite.Group()
    lava = pygame.sprite.Group()
    key_group = pygame.sprite.Group()
    enemy = pygame.sprite.Group()
    hearts = pygame.sprite.Group()
    potion = pygame.sprite.Group()
    potion_mark = pygame.sprite.Group()
    Live(500, 10)
    Live(550, 10)
    Live(600, 10)
    running = True
    player, level_x, level_y = generate_level(load_level('level_{}.txt'.format(str(level))))
    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    pygame.mixer.music.load('Sound_fon.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.1)
    while running:
        up = False
        # в player_group.update() передаются три булевых знания, обозночающие смену направления, стрельбу и прыжок
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                running = False
            elif i.type == pygame.KEYDOWN:
                if i.key == pygame.K_LEFT:
                    motion = 'left'
                    player_group.update(True, False, False)
                    up = True
                elif i.key == pygame.K_RIGHT:
                    motion = 'right'
                    player_group.update(True, False, False)
                    up = True
                elif i.key == pygame.K_z:
                    player_group.update(False, True, False)
                    up = True
                elif i.key == pygame.K_SPACE:
                    player_group.update(False, False, True)
                    up = True
            elif i.type == pygame.KEYUP:
                if i.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    motion = 'stop'
                    player_group.update(True, False, False)
                    up = True
        if up is False:
            player_group.update(False, False, False)
        for sprite in all_sprites:
            if sprite.tile_type != 'lava':
                sprite.rect.x -= 3
        for sprite in player_group:
            sprite.rect.x -= 3
            coords[0] -= 3
        if pain is True:
            hearts.empty()
            for i in range(life):
                Live(500 + 50 * i, 10)
        pain = False
        bullets_en.update()
        bullets.update()
        enemy.update()
        lava.update()
        potion.update()
        key_group.update()
        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)
        enemy.draw(screen)
        potion_mark.draw(screen)
        bullets.draw(screen)
        hearts.draw(screen)
        key_group.draw(screen)
        bullets_en.draw(screen)
        lava.draw(screen)
        player_group.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
