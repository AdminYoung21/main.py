# импорт библиотек
import sys
import pygame
import os
import pygame_menu

# инициализация
pygame.init()
FPS = 200

# размеры окна:
size = WIDTH, HEIGHT = 1000, 700

# Подключаю мелодию
pygame.mixer.init()
sound = pygame.mixer.Sound("data/music/fonk3_game.mp3")
# Громкость мелодии
sound.set_volume(0)
sound_accident = pygame.mixer.Sound("data/music/accident_avto.mp3")
sound_accident.set_volume(0)
sound_menu = pygame_menu.sound.Sound()
sound_menu.set_sound(pygame_menu.sound.SOUND_TYPE_OPEN_MENU, 'data/music/fonk1_menu.ogg')
sound_after_lvl = pygame.mixer.Sound("data/music/after_lvl.mp3")
sound_after_lvl.set_volume(0.7)

# группы спрайтов
all_sprites = pygame.sprite.Group()
cars_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
finish_group = pygame.sprite.Group()


def load_Image(name, colorkey=None):
    """подгрузка изображений из папки data/image"""
    fullname = os.path.join('data/image', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


class Hero(pygame.sprite.Sprite):
    # передаём Измене́ние
    image = load_Image("carHero.png")
    # Измене́ние Измене́ния
    image = pygame.transform.scale(image, (10, 160))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Hero.image
        self.rect = self.image.get_rect()
        self.rect.x = 850
        self.rect.y = 100
        self.step = 10
        self.Win = False

    def update(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.step
        if key[pygame.K_RIGHT] and self.rect.x < WIDTH - 120:
            self.rect.x += self.step


class FinishLn(pygame.sprite.Sprite):
    # передаём изображение
    image = load_Image("finish.png")
    # Измене́ние изображения
    image = pygame.transform.scale(image, (1000, 100))

    def __init__(self, x, y, *group):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно!!!
        super().__init__(*group)
        self.image = FinishLn.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # движение с проверкой на пересечение финиша
    def update(self, target, target_group, sound_after_lvl):
        self.rect.y -= 1
        if pygame.sprite.spritecollide(self, player_group, True):
            sound_after_lvl.play()
            target.Win = True


class Car(pygame.sprite.Sprite):
    # передаём изображение
    images = load_Image("carHuman.png")
    police = load_Image("police.png")
    # Измене́ние изображения
    police = pygame.transform.scale(police, (180, 60))
    images = pygame.transform.scale(images, (120, 160))

    def __init__(self, x, y, type, *group):
        super().__init__(*group)
        if type == "carHuman":
            self.image = Car.images
        else:
            self.image = Car.police
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # движение с проверкой на столкновение
    def update(self, target, target_group, sound_accident):
        self.move()
        if pygame.sprite.spritecollide(self, player_group, True):
            sound_accident.play()

    def move(self):
        self.rect.y -= 1
        if self.rect.y < -200:
            self.kill()


def load_level(filename):
    filename = "level/data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '$':
                Car(x * 50, y * 100 + HEIGHT, "police", cars_group, all_sprites)
            elif level[y][x] == '#':
                Car(x * 100, y * 100 + HEIGHT, "carHuman", cars_group, all_sprites)
            elif level[y][x] == '!':
                print(x, y)
                FinishLn(0, y * 100 + HEIGHT, finish_group, all_sprites)


def terminate():
    """Выйти из игры"""
    pygame.quit()
    sys.exit()


# меню
BACKGROUND_MENU = pygame_menu.baseimage.BaseImage(
    image_path="data/image/fon_menu.jpg",
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY,
    drawing_offset=(0, 0)
)
# создаём свою тему для меню
my_theme = pygame_menu.themes.Theme(
    # transparent background
    background_color=BACKGROUND_MENU,
    title_background_color=(0, 0, 0),
    widget_font=pygame_menu.font.FONT_OPEN_SANS_ITALIC,
    title_font=pygame_menu.font.FONT_OPEN_SANS_ITALIC,

    title_font_shadow=True,
    widget_padding=25,
    widget_font_color=(255, 255, 0),
)


def start_Menu(theme=my_theme):
    """ Запуск меню """
    menu = pygame_menu.Menu('My car', WIDTH, HEIGHT, theme=my_theme)
    # Apply on menu and all sub-menus
    menu.set_sound(sound_menu, recursive=True)
    sound_menu.play_open_menu()
    menu.add.button("Play 1lvl", start_Game)
    menu.add.button("Play 2lvl",lambda: start_Game("2lvl.txt"))
    menu.add.button("Exit", pygame_menu.events.EXIT)
    # цикл меню
    menu.mainloop(screen)


BACK_MENU = pygame_menu.baseimage.BaseImage(
    image_path="data/image/Game-Over.jpg",
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY,
    drawing_offset=(0, 0)
)
# создаём свою тему для меню
my_themeOver = pygame_menu.themes.Theme(
    # transparent background
    background_color=BACK_MENU,
    title_background_color=(0, 0, 0),
    widget_font=pygame_menu.font.FONT_OPEN_SANS_ITALIC,
    title_font=pygame_menu.font.FONT_OPEN_SANS_ITALIC,
    widget_offset=(60, HEIGHT - 300),

    title_font_shadow=True,
    widget_padding=25,
    widget_font_color=(255, 255, 0),
)


def gameOver_Menu(theme=my_themeOver):
    """ Запуск Game_Over(проиграл) меню """
    menu = pygame_menu.Menu('', WIDTH, HEIGHT, theme=theme)
    menu.add.button("Exit", pygame_menu.events.EXIT)
    # цикл меню
    menu.mainloop(screen)


Ban_MENU = pygame_menu.baseimage.BaseImage(
    image_path="data/image/Win.jpg",
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_REPEAT_XY,
    drawing_offset=(0, 0)
)
Ban_MENU.resize(WIDTH, HEIGHT)
# создаём свою тему для меню
my_themeWin = pygame_menu.themes.Theme(
    # transparent background
    background_color=Ban_MENU,
    title_background_color=(0, 0, 0),
    widget_font=pygame_menu.font.FONT_OPEN_SANS_ITALIC,
    title_font=pygame_menu.font.FONT_OPEN_SANS_ITALIC,
    widget_offset=(60, HEIGHT - 300),

    title_font_shadow=True,
    widget_padding=25,
    widget_font_color=(255, 255, 0),
)


def gameWin_Menu(theme=my_themeWin):
    """ Запуск выйграл меню """
    menu = pygame_menu.Menu('', WIDTH, HEIGHT, theme=theme)
    menu.add.button("Exit", pygame_menu.events.EXIT)
    # цикл меню
    menu.mainloop(screen)


def start_Game(level="1lvl.txt"):
    pygame.mouse.set_visible(False)
    img_cursor = pygame.image.load("data/image/mouse.png")

    hero = Hero(player_group, all_sprites)
    car = Car(540, HEIGHT, "police", cars_group, all_sprites)

    bg = pygame.image.load("data/image/fon.jpg")
    # Измене́ние изображения
    bg = pygame.transform.scale(bg, (1000, 700))
    bgs = []
    bgs.append(pygame.Rect(0, 0, 1100, 700))

    img_bg = load_Image('fon.jpg')
    # Измене́ние изображения
    img_bg = pygame.transform.scale(img_bg, (1000, 700))
    generate_level(load_level(level))

    # время
    clock = pygame.time.Clock()

    running = True
    while running:
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                terminate()

        # отрисовка и изменение свойств объектов
        screen.fill((255, 255, 255))
        cars_group.update(hero, player_group, sound_accident)

        if len(player_group.sprites()) == 0:
            sound.stop()
            sound_accident.play()
            running = False
            gameOver_Menu()

        player_group.update()
        finish_group.update(hero, player_group, sound_after_lvl)

        if hero.Win:
            gameWin_Menu()
        sound.play()

        for i in range(len(bgs) - 1, - 1, - 1):
            bg = bgs[i]
            bg.y -= 1
            if bg.bottom > HEIGHT:
                bgs.remove(bg)
            if bgs[len(bgs) - 1].bottom <= HEIGHT:
                bgs.append(pygame.Rect(0, bgs[len(bgs) - 1].bottom, 1100, 700))
        for bg in bgs:
            screen.blit(img_bg, bg)

        pos = pygame.mouse.get_pos()

        # в главном игровом цикле
        all_sprites.draw(screen)
        screen.blit(img_cursor, pos)

        # обновление экрана
        pygame.display.flip()
        clock.tick(1000)


if __name__ == '__main__':
    pygame.display.set_caption('My PyGame')
    # screen — холст, на котором нужно рисовать:
    screen = pygame.display.set_mode(size)
    start_Menu()