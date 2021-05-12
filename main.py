import os
import random

import pygame


class SpaceShip(pygame.sprite.Sprite):
    """oyuncu karakteri uzay gemisi, skor,yakıt,can,ateşleme ve hareket fonksiyonları"""

    def __init__(self, collide, rangex=500, rangey=500):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/spaceship.png')
        self.score = 0
        self.fuel = 200
        self.lives = 3
        self.x = 200
        self.y = 250
        self.collide = collide
        self.laser = None
        self.rocket = None
        self.rocketready = False
        self.shootable = False
        self.maxTick = 10
        self.tick = self.maxTick
        self.maxRocket = 30
        self.rangex = rangex
        self.rangey = rangey
        self.rockettick = self.maxRocket

    def update(self, *args):
        self.speedx = 0
        self.speedy = 0
        if self.tick == 0 and self.fuel >= 1:
            self.shootable = True
            self.tick = self.maxTick
        else:
            self.tick -= 1
        if self.rockettick == 0 and self.fuel >= 2:
            self.rocketready = True
            self.rockettick = self.maxRocket
        else:
            self.rockettick -= 1
        pygame.event.get()
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_SPACE]:
            if self.shootable:
                self.shoot()
                self.shootable = False
        if keystate[pygame.K_r]:
            if self.rocketready:
                self.missile()
                self.rocketready = False
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        self.rect.x += self.speedx
        if self.rect.right > self.rangex:
            self.rect.right = self.rangex
        if self.rect.left < 0:
            self.rect.left = 0
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
        self.rect.y += self.speedy
        if self.rect.y > self.rangey:
            self.rect.y = self.rangey
        if self.rect.y < 0:
            self.rect.y = 0

    def shoot(self):
        """mermi ateşleme fonksiyonu"""
        laser = Shoot(self.rect.right, self.rect.center[1], self.rangex)
        self.collide.add(laser)
        self.fuel -= 1

    def missile(self):
        """roket ateşleme fonksiyonu"""
        rocket = Rockets(self.rect.right, self.rect.center[1], self.rangey)
        self.collide.add(rocket)
        self.fuel -= 2


class Lives(pygame.sprite.Sprite):
    """karakterin canları"""

    def __init__(self, lives=3):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/spaceship.png')
        self.rect.x = (lives - 1) * 64
        self.rect.y = 10


class Fuels(pygame.sprite.Sprite):
    """yakıt sınıfı"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/fuel.png')

    def update(self, *args):
        self.rect.x += -1


class Shoot(pygame.sprite.Sprite):
    """mermi sınıfı ve hareket fonksiyonu"""

    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/shot.gif')
        self.rect.x = x
        self.rect.y = y
        self.width = width
        # self.sndHit1 = pygame.mixer.Sound('data/laser.wav')
        # hit

    def update(self):
        self.rect.x += 25
        if self.rect.x > self.width:
            self.kill()


class Rockets(pygame.sprite.Sprite):
    """karakterin ateşleyebildiği roket sınıfı ve hareket fonksiyonu"""

    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/rocket.png')
        self.rect.x = x
        self.rect.y = y
        self.width = width
        # self.rcktHit1 = pygame.mixer.Sound('data/boom.wav')

    def update(self):
        # self.count = 0
        # self.rect.x = 20
        self.rect.x += 2
        self.rect.y += 10
        if self.rect.y > self.width:
            self.kill()
        # if self.count > 8:
        #     self.rect.x +=0


class TheEndGame(pygame.sprite.Sprite):
    """oyun sonu için bitiş bayrağı olan taş."""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/stone.png')

    def update(self, *args):
        self.rect.x += -1

    def end(self):
        if self.rect.x < 200:
            return True
        return False


class Stone(pygame.sprite.Sprite):
    """mapi oluşturan taş sınıfı"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/stone.png')

    def update(self, *args):
        self.rect.x += -1


class Enemy1(pygame.sprite.Sprite):
    """1.düşman, 1.25 ve 2.5 arasında rastgele bir hızla ilerler"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/enemy1.png')

    def update(self, *args):
        self.rect.x -= random.uniform(1.25, 2.5)


class Enemy2(pygame.sprite.Sprite):
    """ateş topu, 2.düşman"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/fireball.png')

    def update(self, *args):
        self.rect.x += -5


class Enemy3(pygame.sprite.Sprite):
    """3.düşman (roket) sınıfı, ve karakter rokete yaklaşınca ateşleme fonksiyonu"""

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/enemy3.png')

    def update(self):
        self.rect.x -= 1
        if self.rect.x < random.randrange(0, 300):
            self.rect.y -= 5


class Space(pygame.sprite.Sprite):
    """arka plandaki uzay fonu ve hareket etme fonksiyonu"""

    def __init__(self, width=960):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/space.png')
        self.x = 0
        self.y = 250
        self.dx = 5
        self.width = width
        self.reset()

    def update(self):
        self.rect.center = (self.x, self.y)
        self.x -= self.dx
        print(self.x, self.width)
        if self.x == 0:
            self.reset()

    def reset(self):
        self.x = self.width


class Background(pygame.sprite.Sprite):
    def __init__(self, number, *args):
        self.image, self.rect = load_png('images/space.png')
        self._layer = -10
        pygame.sprite.Sprite.__init__(self, *args)
        self.moved = 0
        self.number = number
        self.rect.x = self.rect.width * self.number

    def update(self):
        self.rect.move_ip(-5, 0)
        self.moved += 5
        if self.moved >= self.rect.width:
            self.rect.x = self.rect.width * self.number
            self.moved = 0


class Explosion(pygame.sprite.Sprite):
    """Patlama sınıfı."""

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.explosion_anim = self.explosionAnim()
        self.image = self.explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

    def explosionAnim(self):
        """Patlama efektlerini gif haline getirir."""
        explosion_anim = {}
        explosion_anim['sm'] = []

        WHITE = (255, 255, 255)
        for i in range(9):
            filename = 'regularExplosion0{}.png'.format(i)
            img_dir = os.path.join(os.path.dirname(__file__), 'data/images')
            img = pygame.image.load(os.path.join(img_dir, filename))
            img.set_colorkey(WHITE)
            img_sm = pygame.transform.scale(img, (32, 32))
            explosion_anim['sm'].append(img_sm)

        return explosion_anim


def load_png(name):
    """ Image dosyalarini okumat"""
    fullname = os.path.join('data', name)

    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as error:
        print('Cannot load image:', fullname)
        raise (SystemExit, error)
    return image, image.get_rect()


def draw_text(surf, text, size, x, y):
    """Ekrana Yazi yazdirma"""
    font_name = pygame.font.match_font('arial')
    WHITE = (255, 255, 255)
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
