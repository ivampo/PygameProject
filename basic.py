import os
import sys
import pygame

width = 450
height = 400

pygame.init()
size = width, height
screen = pygame.display.set_mode(size)
fps = 60
clock = pygame.time.Clock()
points = 0


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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
    filename = "data/" + filename
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


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')
diamond_image = load_image('star.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, n):
        if n == 1:
            self.rect = self.rect.move(0, -50)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(0, 50)
        if n == 2:
            self.rect = self.rect.move(0, 50)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(0, -50)
        if n == 3:
            self.rect = self.rect.move(-50, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(50, 0)
        if n == 4:
            self.rect = self.rect.move(50, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(-50, 0)


class Diamond(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(diamond_group, all_sprites)
        self.image = diamond_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 10)

    def update(self, n):
        global points
        if pygame.sprite.spritecollideany(self, player_group):
            points += 1
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


player = None

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
diamond_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    diamond_coords = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                tile = Tile('wall', x, y)
                walls_group.add(tile)
            elif level[y][x] == '@':
                player_x = x
                player_y = y
                Tile('empty', x, y)
            elif level[y][x] == '&':
                diamond_coords.append([x, y])
                Tile('empty', x, y)
    new_player = Player(player_x, player_y)
    for diamond in diamond_coords:
        Diamond(diamond[0], diamond[1])
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map.txt'))

camera = Camera()
# start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                all_sprites.update(1)
            if event.key == pygame.K_DOWN:
                all_sprites.update(2)
            if event.key == pygame.K_LEFT:
                all_sprites.update(3)
            if event.key == pygame.K_RIGHT:
                all_sprites.update(4)
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)
    clock.tick(fps)
    pygame.display.flip()

pygame.quit()