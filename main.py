import pygame
from pygame.locals import *
import pickle
from os import path

pygame.init()

#фоновая музыка
pygame.mixer.init()
pygame.mixer.music.load("DRAMERSON_-_Gachimuchi_Will_Be_Fine_73255331.mp3")
pygame.mixer.music.play(-1)

#звуковые эффекты
jump_fx = pygame.mixer.Sound('woo.wav')
jump_fx.set_volume(1)
game_over_fx = pygame.mixer.Sound('oh-shit-iam-sorry.wav')
game_over_fx.set_volume(1)
exit_fx = pygame.mixer.Sound('boy-next-door.wav')
exit_fx.set_volume(1)
game2_over_fx = pygame.mixer.Sound('oh-yes-sir.wav')
game2_over_fx.set_volume(1)


clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('славянские игры')

# игровые переменные
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 8
score = 0

# загрузка картнок(не все тут)
sun_img = pygame.image.load('sun.png')
bg_img = pygame.image.load('sky.png')
restart_img = pygame.image.load('restart_btn.png')
start_img = pygame.image.load('start_btn.png')
exit_img = pygame.image.load('exit_btn.png')


#функция сброса уровня
def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    #загрузка данных уровня и создание мира
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world



class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #положение мыши на экране
        pos = pygame.mouse.get_pos()

        #условия наведения курсора мыши и щелчка
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #рисование кнопок
        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            #получение нажатия клавиш
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #обработка анимации
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            #добавление гравитации
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # проверка колизий (столкновений)
            self.in_air = True
            for tile in world.tile_list:
                # проверка колизий по иксу(Х)
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #проверка колизий по игрику (У)
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #проверка прыжков
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # проверка падений
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # нет ли столкновений с врагами + звуки
            if pygame.sprite.spritecollide(self, blob_group, False):
                game_over = -1
                game2_over_fx.play()

            # нет ли столкновения с лавой + звуки
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # нет ли столкновения с выходом + звуки
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
                exit_fx.play()


            # обновление координат игрока
            self.rect.x += dx
            self.rect.y += dy


        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        # выведите игрока на экран
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'kj{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('ghostt.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        # снова загрузка картинок
        dirt_img = pygame.image.load('dirt.png')
        grass_img = pygame.image.load('dirt.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)

                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('boy.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



# расположение и создание кнопок на экране
restart_button = Button(screen_width // 2 - 80, screen_height // 2 + 20, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

#зфгрузка данных уровня (lvl data)
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)

world = World(world_data)

run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            blob_group.update()

        blob_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # если игрок умер
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        # если игрок завершил уровень
        if game_over == 1:
            # перезагрузите игру и переходите на следующий уровень
            level += 1
            if level <= max_levels:
                # сброс уровня
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()