import os
import random
import numpy as np
from math import atan2, degrees, dist
import pygame
from pynput.keyboard import Key, Controller

keyboard = Controller()


class SpaceShip(pygame.sprite.Sprite):
    """oyuncu karakteri uzay gemisi, skor,yakıt,can,ateşleme ve hareket fonksiyonları"""

    def __init__(self, collide, rangex=500, rangey=500):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_png('images/spaceship.png')
        self.score = 0
        self.fuel = 200
        self.lives = 1
        self.rect.x = 0
        self.rect.y = (rangey // 2) - 40
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
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE]:
            self.shoot()
        if keystate[pygame.K_r]:
            self.missile()
        if keystate[pygame.K_LEFT]:
            self.left()
        if keystate[pygame.K_RIGHT]:
            self.right()

        if self.rect.right > self.rangex - 10:
            self.rect.right = self.rangex - 10
        if self.rect.left < 0:
            self.rect.left = 0
        if keystate[pygame.K_UP]:
            self.up()
        if keystate[pygame.K_DOWN]:
            self.down()
        # self.rect.y += self.speedy
        if self.rect.y > self.rangey:
            self.rect.y = self.rangey
        if self.rect.y < 0:
            self.rect.y = 0

    def radar(self):
        pass

    def up(self):
        self.speedy = -8
        self.rect.y += self.speedy

    def down(self):
        self.speedy = 8
        self.rect.y += self.speedy

    def right(self):
        self.speedx = 8
        self.rect.x += self.speedx

    def left(self):
        self.speedx = -8
        self.rect.x += self.speedx

    def shoot(self):
        """mermi ateşleme fonksiyonu"""
        if self.shootable:
            laser = Shoot(self.rect.right, self.rect.centery, self.rangex)
            self.collide.add(laser)
            self.fuel -= 1
            self.score -= 1
            self.shootable = False

    def missile(self):
        """roket ateşleme fonksiyonu"""
        if self.rocketready:
            rocket = Rockets(self.rect.right, self.rect.center[1], self.rangey)
            self.collide.add(rocket)
            self.fuel -= 2
            self.score -= 2
            self.rocketready = False

    def play(self, predictions):
        # print(predictions)
        if predictions[0] > 0.5:
            # print("tried to shoot")
            self.shoot()
        if predictions[1] > 0.5:
            # print("tried to missile")
            self.missile()
        if predictions[2] > 0.5:
            # print("tried to go up")
            self.up()
        if predictions[3] > 0.5:
            # print("tried to go down")
            self.down()
        if predictions[4] > 0.5:
            # print("tried to go right")
            self.right()
        if predictions[5] > 0.5:
            # print("tried to go left")
            self.left()


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


def get_angle(pointA, pointB):
    changeInX = pointB[0] - pointA[0]
    changeInY = pointB[1] - pointA[1]
    return degrees(atan2(changeInY, changeInX))


def get_distance(pointA, pointB):
    return dist(pointA, pointB)


def get_coinformation(spaceship: pygame.sprite.Sprite, targets: pygame.sprite.Group):
    infos = []
    for target in targets:
        # angle = get_angle(spaceship.rect.right, target.rect.left)
        distance = dist(spaceship.rect.right, target.rect.left)
        infos.append(distance)
    #     infos.append((distance, angle))
    # infos.sort(key=lambda x: x[0])
    infos.sort()
    return infos


def get_distances(spaceship: pygame.sprite.Sprite, targets: pygame.sprite.Group):
    infos = []
    for target in targets:
        distance_x = spaceship.rect.right - target.rect.left
        distance_y = spaceship.rect.centery - target.rect.centery
        infos.append((distance_x, distance_y))
    infos.sort(key=lambda x: x[0])
    return infos


def get_closest(spaceship: pygame.sprite.Sprite, targets: pygame.sprite.Group):
    infos = []
    closest_dist = 999999
    closest_obj = None
    for target in targets:
        dist = get_distance(spaceship.rect, target.rect)
        if dist < closest_dist \
                and spaceship.rect.centery - target.rect.centery < 0 \
                and spaceship.rect.left - target.rect.left < 0:
            closest_obj = target
            closest_dist = dist
    return closest_obj


def get_closest_n(spaceship: pygame.sprite.Sprite, targets: pygame.sprite.Group, n):
    infos = []
    closest_dists = [999 for n in range(n)]
    closest_objs = [None for n in range(n)]
    for target in targets:
        dist = get_distance(spaceship.rect, target.rect)
        max_ind = np.argmax(closest_dists)
        if dist < closest_dists[int(max_ind)] \
                and spaceship.rect.centery - target.rect.centery < 0 \
                and spaceship.rect.left - target.rect.left < 0 \
                and target.rect.left < 800:
            closest_objs.pop(int(max_ind))
            closest_objs.insert(int(max_ind), target)
            closest_dists.pop(int(max_ind))
            closest_dists.insert(int(max_ind), dist)
    return closest_objs


def get_positions(targets: pygame.sprite.Group):
    infos = [target.rect.center for target in targets]
    # for target in targets:
    #     infos.append(target.rect.center)
    return infos


def lineRectIntersectionPoints(line, rect):
    """ Get the list of points where the line and rect
        intersect,  The result may be zero, one or two points.

        BUG: This function fails when the line and the side
             of the rectangle overlap """

    def linesAreParallel(x1, y1, x2, y2, x3, y3, x4, y4):
        """ Return True if the given lines (x1,y1)-(x2,y2) and
            (x3,y3)-(x4,y4) are parallel """
        return (((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)) == 0)

    def intersectionPoint(x1, y1, x2, y2, x3, y3, x4, y4):
        """ Return the point where the lines through (x1,y1)-(x2,y2)
            and (x3,y3)-(x4,y4) cross.  This may not be on-screen  """
        # Use determinant method, as per
        # Ref: https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        Px = ((((x1 * y2) - (y1 * x2)) * (x3 - x4)) - ((x1 - x2) * ((x3 * y4) - (y3 * x4)))) / (
                ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        Py = ((((x1 * y2) - (y1 * x2)) * (y3 - y4)) - ((y1 - y2) * ((x3 * y4) - (y3 * x4)))) / (
                ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4)))
        return Px, Py

    ### Begin the intersection tests
    result = []
    line_x1, line_y1, line_x2, line_y2 = line  # split into components
    pos_x, pos_y, width, height = rect

    ### Convert the rectangle into 4 lines
    rect_lines = [(pos_x, pos_y, pos_x + width, pos_y), (pos_x, pos_y + height, pos_x + width, pos_y + height),
                  # top & bottom
                  (pos_x, pos_y, pos_x, pos_y + height),
                  (pos_x + width, pos_y, pos_x + width, pos_y + height)]  # left & right

    ### intersect each rect-side with the line
    for r in rect_lines:
        rx1, ry1, rx2, ry2 = r
        if (not linesAreParallel(line_x1, line_y1, line_x2, line_y2, rx1, ry1, rx2, ry2)):  # not parallel
            pX, pY = intersectionPoint(line_x1, line_y1, line_x2, line_y2, rx1, ry1, rx2,
                                       ry2)  # so intersecting somewhere
            pX = round(pX)
            pY = round(pY)
            # Lines intersect, but is on the rectangle, and between the line end-points?
            if (rect.collidepoint(pX, pY) and
                    pX >= min(line_x1, line_x2) and pX <= max(line_x1, line_x2) and
                    pY >= min(line_y1, line_y2) and pY <= max(line_y1, line_y2)):
                # pygame.draw.circle( surface, "WHITE", ( pX, pY ), 4 )
                result.append((pX, pY))  # keep it
                if (len(result) == 2):
                    break  # Once we've found 2 intersection points, that's it
    return result


def check_linecol(spaceship: pygame.sprite.Sprite, targets: pygame.sprite.Group, line):
    # Does the line <player> to <the road of missile> intersect any obstacles?
    line_of_sight = [spaceship.rect.right, spaceship.rect.centery, *line]
    found = True
    coords = []
    for target in targets:
        # is anyting blocking the line-of-sight?
        intersection_points = lineRectIntersectionPoints(line_of_sight, target.rect)
        if (len(intersection_points) > 0):
            found = False
            coords = intersection_points
            return coords
            # break  # seen already

    # if (found):
    #     # pygame.draw.line(window, WHITE, player_centre, npc_centre)
    #     return coords
    # else:
    #     # pygame.draw.line(window, GREY, player_centre, npc_centre)
    #     return "WHITE"


def calculate_missile_points(spaceship: pygame.sprite.Sprite):
    xpos = spaceship.rect.right
    ypos = spaceship.rect.centery
    Py = 640 - ypos
    Px = xpos
    k = Py // 10
    Sx = Px + (k * 2)
    Sy = 640
    return Sx, Sy


def calculate_bullet_points(spaceship: pygame.sprite.Sprite):
    # xpos = spaceship.rect.right
    ypos = spaceship.rect.centery

    # Py = 640 - ypos
    # Px = xpos
    # k = Py // 10
    # Sx = Px + (k * 2)
    # Sy = 640
    return 800, ypos
