import os
import sys
import pygame
import numpy

width = 450
height = 400

pygame.init()
size = width, height
screen = pygame.display.set_mode(size)
fps = 15
clock = pygame.time.Clock()
points = 0
health = 100


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename =  filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


def color_surface(surface, red, green, blue):
    arr = pygame.surfarray.pixels3d(surface)
    arr[:,:,0] = red
    arr[:,:,1] = green
    arr[:,:,2] = blue


def draw_points(screen):
    font = pygame.font.Font(None, 30)
    text_points = font.render(f"Points: {points}", True, (255, 255, 255))
    text_health = font.render(f"Health: {health}", True, (255, 255, 255))
    max_width = max(text_points.get_width(), text_health.get_width())
    text_x = width - max_width - 10
    text_y = 5
    screen.fill((0, 0, 0), (text_x - 5, 0, text_x + max_width, text_y + text_points.get_height() * 2 + 5))
    screen.blit(text_points, (text_x, text_y))
    screen.blit(text_health, (text_x, text_y + 25))


tile_images = {
    'wall': pygame.transform.scale(load_image('tree.png'), (50, 50)),
    'empty': pygame.transform.scale(load_image('grass1.png'), (50, 50))
}
player_image = load_image('mario.png')
good_plant_image = load_image('good_plant.png')
good_plant_image = pygame.transform.scale(good_plant_image, (26, 26))
bad_plant_image = load_image('bad_plant1.png')
enemy_image = load_image('star.png')
bad_plant_image = pygame.transform.scale(bad_plant_image, (26, 26))

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(
            tile_width * x + 2, tile_height * y)
        self.last_n = 0
        self.dic = {1: 16, 2: 4, 3: 8, 4: 12}

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def step(self, n=0):
        if n == 1:
            self.rect = self.rect.move(0, -10)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(0, 10)
        if n == 2:
            self.rect = self.rect.move(0, 10)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(0, -10)
        if n == 3:
            self.rect = self.rect.move(-10, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(10, 0)
        if n == 4:
            self.rect = self.rect.move(10, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(-10, 0)
        if n:
            self.image_step(n)
            self.image = self.frames[self.cur_frame]

    def image_step(self, n):
        if self.last_n == n:
            self.cur_frame = (self.cur_frame + 1) % self.dic[n]
            if self.cur_frame < self.dic[n] - 4:
                self.cur_frame += self.dic[n] - 4
        else:
            self.cur_frame = self.dic[n] - 4
        self.last_n = n

    def turn_red(self):
        orig_surface = self.image
        orig_surface.convert_alpha()
        colored_surface = orig_surface.copy()
        color_surface(colored_surface, 255, 100, 100)
        self.image = colored_surface


class GoodPlant(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(plant_group, all_sprites)
        self.image = good_plant_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 12, tile_height * pos_y + 12)

    def update(self):
        global points
        if pygame.sprite.spritecollideany(self, player_group):
            points += 1
            self.kill()


class BadPlant(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(plant_group, all_sprites)
        self.image = bad_plant_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 12, tile_height * pos_y + 12)

    def update(self):
        global health
        if pygame.sprite.spritecollideany(self, player_group):
            health -= 10
            player.turn_red()
            self.kill()


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, directionn):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.direction = [directionn, 1]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 10)

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            pass
            # end_screen()
        if self.direction[0] == 'h':
            self.rect = self.rect.move(self.direction[1] * 2, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.direction[1] *= -1
                self.rect = self.rect.move(self.direction[1] * 4, 0)

        else:
            self.rect = self.rect.move(0, self.direction[1] * 1)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.direction[1] *= -1
                self.rect = self.rect.move(0, self.direction[1] * 2)


player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
plant_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    good_plant_coords = []
    bad_plant_coords = []
    enemy_coords = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('empty', x, y)
                tile = Tile('wall', x, y)
                walls_group.add(tile)
            elif level[y][x] == '@':
                player_x = x
                player_y = y
                Tile('empty', x, y)
            elif level[y][x] == '&':
                good_plant_coords.append([x, y])
                Tile('empty', x, y)
            elif level[y][x] == '+':
                bad_plant_coords.append([x, y])
                Tile('empty', x, y)
            elif level[y][x] == 'h':
                enemy_coords.append([x, y, 'h'])
                Tile('empty', x, y)
            elif level[y][x] == 'v':
                enemy_coords.append([x, y, 'v'])
                Tile('empty', x, y)
    new_player = Player(pygame.transform.scale(load_image('hero.png'), (184, 184)), 4, 4, player_x, player_y)
    for plant in good_plant_coords:
        GoodPlant(plant[0], plant[1])
    for plant in bad_plant_coords:
        BadPlant(plant[0], plant[1])
    for i in enemy_coords:
        Enemy(i[0], i[1], i[2])
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map.txt'))

camera = Camera()
# start_screen()
running = True
motion = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                motion = 1
            if event.key == pygame.K_DOWN:
                motion = 2
            if event.key == pygame.K_LEFT:
                motion = 3
            if event.key == pygame.K_RIGHT:
                motion = 4
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT,
                             pygame.K_UP, pygame.K_DOWN]:
                motion = 0
    player.step(motion)
    all_sprites.update()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    draw_points(screen)
    clock.tick(fps)
    pygame.display.flip()

pygame.quit()