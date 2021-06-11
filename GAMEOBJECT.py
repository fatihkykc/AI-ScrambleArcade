import pickle
import os
#
import itertools
from main import *
import neat, pygame


class GameObject:
    """Oyun objesi."""

    def __init__(self, genomes, config, height=640, width=800, keepgoing=True, level=1, game_over=False, fps=9999,
                 screenshow=False, inputNum=20):
        if not screenshow:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        self.screenshow = screenshow
        pygame.init()
        self.white = (255, 255, 255)
        pygame.mixer.init()
        self.currentLevel = level
        self.fps = fps
        self.width = width
        self.height = height
        self.keepgoing = keepgoing
        self.g = genomes
        self.config = config
        self.nets = []
        self.ge = []
        self.spaceships = []
        self.game_over = game_over
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.xnodePos = [[0 for x in range(inputNum)] for y in range(inputNum * 3)]
        self.ynodePos = [[0 for x in range(inputNum)] for y in range(inputNum * 3)]
        self.nodePos = list(zip(self.xnodePos, self.ynodePos))
        self.inputNum = inputNum
        self.inputImage = [[0 for i in range(self.inputNum)] for j in range(self.inputNum * 3)]
        for x in range(0, inputNum):
            for y in range(0, inputNum):
                if (x % 2 == 0):
                    self.inputImage[x][y] = self.GREEN
                else:
                    self.inputImage[x][y] = self.BLUE
        if self.screenshow:
            self.initScreen()
            self.fillBackground()
            self.blit()
        else:
            self.clock = pygame.time.Clock()
        self.lives = [Lives(1)]
        self.initSprites()
        self.load_data()
        self.update()

    def update(self):
        """Update fonksiyonu her frame de çağrılır."""
        for genome_id, genome in self.g:
            genome.fitness = 0  # start with fitness level of 0
            net = neat.nn.FeedForwardNetwork.create(genome, self.config)
            while self.spaceship.lives >= 0:
                if self.spaceship.lives == 0:
                    # self.game_over = True
                    self.keepgoing = True
                    self.initSprites()
                    self.keepGoing(strt=False)
                    print("Species: " + str(genome_id))
                    break
                    # self.colliders()
                    # self.spriteUpdate()
                    # self.clear()
                    # self.draw()
                    # self.isThisTheEnd()
                    # pygame.display.flip()
                    # self.spaceship.lives=1s
                else:
                    # self.keepgoing = True
                    self.keepGoing()
                    self.colliders()
                    self.spriteUpdate()
                    # ********** INPUTS ************ #
                    # x and y distance with the 5 closest enemies in front
                    # distance with the top and bottom stones
                    closest_rocket = get_closest(self.spaceship, self.enemy3Sprites, self.width)
                    # closest_fuel = get_closest(self.spaceship, self.fuelSprites, self.width)
                    # closest_rocket = get_closest_n(self.spaceship, self.enemy3Sprites, 2)
                    # closest_fuel = get_closest_n(self.spaceship, self.fuelSprites, 2)
                    # closest_stone = get_closest(self.spaceship, self.stoneSprites, self.width)
                    # highest_stone = 0
                    # if closest_stone:
                    #     if closest_stone.rect.top > highest_stone:
                    #         highest_stone = closest_stone.rect.top
                    closest_enemy1s = get_closest_n(self.spaceship, self.enemy1Sprites, 5, self.width)
                    # missile_points = calculate_missile_points(self.spaceship, self.height)
                    # top_points = calculate_top_points(self.spaceship)
                    # bottom_points = calculate_bottom_points(self.spaceship, self.height)
                    bullet_points = calculate_bullet_points(self.spaceship, self.width)
                    # all_sp = pygame.sprite.Group(*self.enemy1Sprites.sprites(), *self.enemy3Sprites.sprites(),
                    #                              *self.fuelSprites.sprites(), *self.stoneSprites.sprites())
                    if closest_rocket:
                        self.enemy1Sprites.add(closest_rocket)
                    # if closest_fuel:
                    #     self.enemy1Sprites.add(closest_fuel)
                    # top_intersections = check_linecol(self.spaceship, all_sp, top_points)
                    # bot_intersections = check_linecol(self.spaceship, all_sp, bottom_points)
                    bullet_intersections = check_linecol(self.spaceship, self.enemy1Sprites, bullet_points)
                    # missile_intersections = check_linecol(self.spaceship, self.enemy1Sprites, missile_points)
                    # enemy1_distanceX, enemy1_distanceY = map(list,
                    #                                          zip(*get_distances(self.spaceship, self.enemy1Sprites)))
                    # fuel_distanceX, fuel_distanceY = map(list,
                    #                                      zip(*get_distances(self.spaceship, self.fuelSprites)))
                    # rocket_distanceX, rocket_distanceY = map(list,
                    #                                          zip(*get_distances(self.spaceship, self.enemy3Sprites)))
                    # print(enemy1_distanceX[0])
                    # enemy1_x, enemy1_y = map(list,
                    #                          zip(*get_positions(self.enemy1Sprites)))
                    # enemy3_x, enemy3_y = map(list,
                    #                          zip(*get_positions(self.enemy3Sprites)))
                    # stone_x, stone_y = map(list,
                    #                        zip(*get_positions(self.stoneSprites)))
                    # fuel_x, fuel_y = map(list, zip(*get_positions(self.fuelSprites)))
                    # print(self.spaceship.rect.right)
                    ces = [[ce.rect.left, ce.rect.right, ce.rect.top, ce.rect.bottom] if ce else [0, 0, 0, 0] for ce in
                           closest_enemy1s]
                    # # print("ces:", ces)
                    # print(np.where(self.inputImage == self.GREEN, 1,
                    #                np.where(self.inputImage == self.RED, 2, 0)))

                    # inp = np.array(self.inputImage, dtype='object').flatten()
                    # [print(x) for x in inp]
                    # inp = [1 if x == self.RED else 2 if x == self.GREEN else 0 for x in inp]
                    # inp = list(map(lambda x: 1 if x==self.RED else 2 if x==self.GREEN else 0, inp))
                    # inp = np.where(np.array(inp) == self.GREEN, 1,
                    #                np.where(np.array(inp) == self.RED, 2, 0))
                    # print(inp)
                    output = net \
                        .activate(
                        (
                            self.spaceship.rect.right, self.spaceship.rect.left,
                            self.spaceship.rect.bottom, self.spaceship.rect.top,
                            ces[0][0], ces[0][1], ces[0][2], ces[0][3],
                            ces[1][0], ces[1][1], ces[1][2], ces[1][3],
                            ces[2][0], ces[2][1], ces[2][2], ces[2][3],
                            ces[3][0], ces[3][1], ces[3][2], ces[3][3],
                            ces[4][0], ces[4][1], ces[4][2], ces[4][3],
                            #         # *enemy3_x, *enemy3_y, *fuel_x, *fuel_y,
                            #         # *[ce.rect.left if ce else 0 for ce in closest_enemy1s],
                            #         # *[ce.rect.top if ce else 0 for ce in closest_enemy1s],
                            #

                            #         # *[ce.rect.left if ce else 0 for ce in closest_rocket],
                            #         # *[ce.rect.top if ce else 0 for ce in closest_rocket],
                            # *[ce.rect.left if ce else 0 for ce in closest_fuel],
                            # *[ce.rect.top if ce else 0 for ce in closest_fuel],
                            # closest_fuel.rect.left if closest_fuel else 0,
                            # closest_fuel.rect.top if closest_fuel else 0,
                            # highest_stone,
                            # [closest_stone.rect.left if closest_stone else 0][0],
                            # [closest_stone.rect.top if closest_stone else 0][0],
                            [closest_rocket.rect.left if closest_rocket else 0][0],
                            [closest_rocket.rect.top if closest_rocket else 0][0],
                            [closest_rocket.rect.bottom if closest_rocket else 0][0],
                            [closest_rocket.rect.right if closest_rocket else 0][0],
                            # [missile_intersections[0][0] if missile_intersections else missile_points[0]][0],
                            # [missile_intersections[0][1] if missile_intersections else missile_points[1]][0],
                            [bullet_intersections[0][0] if bullet_intersections else bullet_points[0]][0],
                            [bullet_intersections[0][1] if bullet_intersections else bullet_points[1]][0],
                            # [top_intersections[0][0] if top_intersections else top_points[0]][0],
                            # [top_intersections[0][1] if top_intersections else top_points[1]][0],
                            # [bot_intersections[0][0] if bot_intersections else bottom_points[0]][0],
                            # [bot_intersections[0][1] if bot_intersections else bottom_points[1]][0]
                        ))
                    # print(self.clock.get_fps())
                    self.spaceship.play(output)
                    genome.fitness = self.spaceship.score
                    if self.screenshow:
                        self.clear()
                        self.draw()
                    # fill_image(inputNum=self.inputNum, inputImg=self.inputImage, HEIGHT=self.height, WIDTH=self.width,
                    #            enemies=[*self.enemy1Sprites.sprites(), *self.enemy3Sprites.sprites()],
                    #            spaceship=self.spaceship)
                    self.isThisTheEnd()
                    self.nets.append(net)
                    self.ge.append(genome)
                    if self.screenshow:
                        pygame.display.flip()

    def isThisTheEnd(self):
        """Oyun sonu"""
        if self.theEndGame.end():
            try:
                print("yeyy")
                self.spaceship.score += 100
                self.spaceship.lives -= 1
                # self.level()
            except Exception as ex:
                pygame.quit()

    def level(self):
        """her bir level için  "-" karakteri mapteki taşları;
        "x" karakteri mapteki fuel, yani yakıt objelerini;
        "e" karakteri düşman füzeleri çağırır."""
        self.isWave1 = True
        self.wave_1()
        # for i in range(8):  ## 8 mobs
        #     mob_element = Mob()
        #     self.mobs.add(mob_element)
        y = 0
        level1 = []
        world = []
        level = open('levels/level' + str(self.currentLevel) + 'a')
        for i in level:
            level1.append(i)
        for row in level1:
            x = 0
            for col in row:
                if col == "-":
                    self.stone = Stone()
                    world.append(self.stone)
                    self.stoneSprites.add(world)
                    self.stone.rect.x = x
                    self.stone.rect.y = y

                if col == "x":
                    self.fuel = Fuels()
                    self.fuelSprites.add(self.fuel)
                    self.fuel.rect.x = x
                    self.fuel.rect.y = y
                if col == "e":
                    self.enemy3 = Enemy3()
                    self.enemy3Sprites.add(self.enemy3)
                    self.enemy3.rect.x = x
                    self.enemy3.rect.y = y

                if col == "]":
                    self.theEndGame = TheEndGame()
                    self.stoneSprites.add(self.theEndGame)
                    self.theEndGame.rect.x = x
                    self.theEndGame.rect.y = y
                x += 32
            y += +32

    def draw_player_fuel(self, surf, x, y, pct):
        """Oyuncu karakterin yakıt seviyesi için görselleştirme."""
        if pct < 0:
            pct = 0
        BAR_LENGTH = 100
        BAR_HEIGHT = 20
        fill = pct * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH * 2, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        if pct > 0.6:
            col = (0, 255, 0)
        elif pct > 0.3:
            col = (255, 255, 0)
        else:
            col = (255, 0, 0)
        pygame.draw.rect(surf, col, fill_rect)
        pygame.draw.rect(surf, self.white, outline_rect, 2)

    def load_data(self, HS_FILE='HighScore'):
        """Oyuncu yüksek skor yaparsa bu skor kaydedilir."""
        # load high score
        self.dir = os.path.dirname(__file__)
        with open(os.path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

    def colliders(self):
        """ana karakterin, mermilerin, füzelerin ve düşmanların çarpışma ve patlama efektleri."""
        # bullet-fuel collider
        fuel_hit_by_bullet = pygame.sprite.groupcollide(self.fuelSprites, self.shootSprites, True, True)
        for hit in fuel_hit_by_bullet:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if fuel_hit_by_bullet:
            self.spaceship.fuel += 10
            self.spaceship.score += 5

        # bullet-enemy collider
        bullethits = pygame.sprite.groupcollide(self.enemy1Sprites, self.shootSprites, True, True)
        for hit in bullethits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if bullethits:
            self.spaceship.score += 10

        # bullet-enemy collider
        bullethits = pygame.sprite.groupcollide(self.enemy3Sprites, self.shootSprites, True, True)
        for hit in bullethits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if bullethits:
            self.spaceship.score += 10

        # player-enemy collider
        spaceshiphits = pygame.sprite.spritecollide(self.spaceship, self.enemy1Sprites, True)
        for hit in spaceshiphits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if spaceshiphits:
            self.spaceship.score -= 50
            self.spaceship.lives -= 1
            self.lives[-1].kill()
            del self.lives[-1]

        # player-mob collider
        # spaceshiphits = pygame.sprite.spritecollide(self.spaceship, self.mobs, True)
        # for hit in spaceshiphits:
        #     expl = Explosion(hit.rect.center, 'sm')
        #     self.explosionSprites.add(expl)
        # if spaceshiphits:
        #     self.spaceship.score -= 50
        #     self.spaceship.lives -= 1
        #     self.lives[-1].kill()
        #     del self.lives[-1]

        # player-enemy collider
        spaceshiphits = pygame.sprite.spritecollide(self.spaceship, self.enemy3Sprites, True)
        for hit in spaceshiphits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if spaceshiphits:
            self.spaceship.score -= 50
            self.spaceship.lives -= 1
            try:
                self.lives[-1].kill()
                del self.lives[-1]
            except:
                print(self.lives)

        # player-enemy collider
        spaceshiphits = pygame.sprite.spritecollide(self.spaceship, self.enemy2Sprites, True)
        for hit in spaceshiphits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if spaceshiphits:
            self.spaceship.score -= 50
            self.spaceship.lives -= 1
            try:
                self.lives[-1].kill()
            except:
                print(self.lives)
            del self.lives[-1]

        # spaceship-ground collider
        spaceshiphitsground = pygame.sprite.spritecollide(self.spaceship, self.stoneSprites, False)
        if spaceshiphitsground:
            self.spaceship.lives = 0
            self.spaceship.score -= 50

        # rocket-ground collider
        rockethitsground = pygame.sprite.groupcollide(self.shootSprites, self.stoneSprites, True, False)
        for hit in rockethitsground:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)

    def initSprites(self):
        """Bütün spriteları(düşman,oyuncu,yakıt,roket,taş,patlama,can) aktifleştirir"""
        # Sprites
        self.space = Background(0)
        self.space1 = Background(1)

        # sprite groups
        self.explosionSprites = pygame.sprite.Group()
        self.systemSprites = pygame.sprite.Group([self.space, self.space1])
        self.liveSprites = pygame.sprite.Group()
        for i in self.lives:
            self.liveSprites.add(i)
        self.enemy1Sprites = pygame.sprite.Group()
        self.enemy2Sprites = pygame.sprite.Group()
        self.enemy3Sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.fuelSprites = pygame.sprite.Group()
        self.shootSprites = pygame.sprite.Group()
        self.stoneSprites = pygame.sprite.Group()
        self.spaceship = SpaceShip(self.shootSprites, self.width, self.height)
        self.userSprites = pygame.sprite.Group(self.spaceship)
        self.rocket = Rockets(self.spaceship.rect.right, self.spaceship.rect.center[1], self.spaceship.rangey)

    def keepGoing(self, isWave1=False, isWave2=False, strt=False):
        """1. ve 2. düşman dalgalarını ve oyun bitiş, açılış ekranını kontrol eder."""
        self.isWave1 = isWave1
        self.isWave2 = isWave2
        if self.keepgoing:
            if strt:
                self.show_strt_screen()
            self.keepgoing = False
            self.lives = [Lives(i) for i in range(1, self.spaceship.lives + 1)]
            self.initSprites()
            self.level()

        if self.game_over:
            self.show_go_screen()
            self.game_over = False
            self.lives = [Lives(i) for i in range(1, self.spaceship.lives + 1)]
            self.initSprites()
            self.currentLevel = 1
            self.level()

        self.clock.tick(self.fps)
        pygame.mouse.set_visible(False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()

    def show_go_screen(self, HS_FILE='HighScore'):
        """oyun bitiş ekranı"""
        self.screen.blit(self.background, (0, 0))
        draw_text(self.screen, "SCRAMBLE!", 64, self.width / 2, self.height / 4)

        draw_text(self.screen, "Nice try, but not enough!", 22,
                  self.width / 2, self.height / 2)
        draw_text(self.screen, "your score is:" + str(self.spaceship.score), 64, self.width / 2, self.height * 3 / 4)
        draw_text(self.screen, "Press any key to play again", 18, self.width / 2, self.height * 8 / 9)
        if self.spaceship.score > self.highscore:
            self.highscore = self.spaceship.score
            draw_text(self.screen, "NEW HIGH SCORE!!", 36, self.width / 2, self.height * 1 / 9)
            with open(os.path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.spaceship.score))
        else:
            draw_text(self.screen, "High Score: " + str(self.highscore), 18, self.width / 2, self.height * 1 / 9)
        pygame.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN and pygame.KEYUP:
                    waiting = False

    def show_strt_screen(self):
        """oyun açılış ekranı"""
        self.screen.blit(self.background, (0, 0))
        draw_text(self.screen, "SCRAMBLE!", 64, self.width / 2, self.height / 4)

        draw_text(self.screen, "Arrow keys move, Space to fire, R to fire rockets", 22,
                  self.width / 2, self.height / 2)
        draw_text(self.screen, "Press a key to begin", 18, self.width / 2, self.height * 8 / 9)
        draw_text(self.screen, "HighScore: " + str(self.highscore), 18, self.width / 2, self.height * 1 / 8)

        pygame.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYUP:
                    waiting = False

    def initScreen(self):
        """ekranı, başlığı ve oyun saatini aktifleştirir."""
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Scramble Game')
        self.clock = pygame.time.Clock()

    def fillBackground(self):
        """arka fonu siyahla doldurur."""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))

    def blit(self):
        """resimleri ekrana blitler."""
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

    def wave_1(self):
        """birinci düşman dalgası için yer ve level konfigurasyonu"""
        # Event loop
        if self.currentLevel == 1 or self.currentLevel == 3:
            for i in range(80):
                self.enemy = Enemy1()
                self.enemy.rect.x = random.randrange(600, 8064, 10)
                self.enemy.rect.y = random.randrange(10, self.height - 70, 10)
                # self.enemySprites.add(self.enemy)
                self.enemy1Sprites.add(self.enemy)
        if self.currentLevel == 2 or self.currentLevel == 3:
            for i in range(50):
                self.enemy2 = Enemy2()
                self.enemy2.rect.x = random.randrange(600, 8064)
                self.enemy2.rect.y = random.randrange(0, self.height // 2 + 50)
                self.enemy2Sprites.add(self.enemy2)

    # def restart(self):
    #     self.

    def clear(self):
        """ekranı temizler."""
        self.systemSprites.clear(self.screen, self.background)
        self.userSprites.clear(self.screen, self.background)
        self.stoneSprites.clear(self.screen, self.background)
        self.enemy2Sprites.clear(self.screen, self.background)
        self.enemy1Sprites.clear(self.screen, self.background)
        self.mobs.clear(self.screen, self.background)
        self.enemy3Sprites.clear(self.screen, self.background)
        self.fuelSprites.clear(self.screen, self.background)
        self.shootSprites.clear(self.screen, self.background)
        self.explosionSprites.clear(self.screen, self.background)
        self.liveSprites.clear(self.screen, self.background)

    def spriteUpdate(self):
        """bütün spriteların update fonksiyonlarını çalıştırır."""
        self.systemSprites.update()
        self.userSprites.update()
        self.stoneSprites.update()
        self.enemy2Sprites.update()
        self.enemy1Sprites.update()
        self.mobs.update()
        self.enemy3Sprites.update()
        self.fuelSprites.update()
        self.shootSprites.update()
        self.explosionSprites.update()
        self.liveSprites.update()

    def draw(self):
        """bütün spriteları ekrana çizer"""
        self.systemSprites.draw(self.screen)
        self.userSprites.draw(self.screen)
        self.stoneSprites.draw(self.screen)
        self.enemy2Sprites.draw(self.screen)
        self.enemy1Sprites.draw(self.screen)
        self.mobs.draw(self.screen)
        self.enemy3Sprites.draw(self.screen)
        self.fuelSprites.draw(self.screen)
        self.shootSprites.draw(self.screen)
        self.explosionSprites.draw(self.screen)
        # self.liveSprites.draw(self.screen)
        # self.draw_player_fuel(self.screen, self.width / 2 - 100, self.height - 50, self.spaceship.fuel / 100)
        # closest_rocket = get_closest(self.spaceship, self.enemy3Sprites, self.width)
        # closest_fuel = get_closest(self.spaceship, self.fuelSprites, self.width)
        # closest_stone = get_closest(self.spaceship, self.stoneSprites, self.width)
        closest_enemy1s = get_closest_n(self.spaceship, self.enemy1Sprites, 5, self.width)
        # missile_points = calculate_missile_points(self.spaceship, self.height)
        bullet_points = calculate_bullet_points(self.spaceship, self.width)
        # missile_intersections = check_linecol(self.spaceship, self.enemy1Sprites, missile_points)
        bullet_intersections = check_linecol(self.spaceship, pygame.sprite.Group(
            [*self.enemy3Sprites, *self.enemy1Sprites]), bullet_points)
        # if closest_rocket:
        #     pygame.draw.line(self.screen, "RED", (self.spaceship.rect.right, self.spaceship.rect.centery),
        #                      (closest_rocket.rect.centerx, closest_rocket.rect.top))
        # # if closest_fuel:
        # #     pygame.draw.line(self.screen, "GREEN", (self.spaceship.rect.right, self.spaceship.rect.centery),
        # #                      (closest_fuel.rect.centerx, closest_fuel.rect.top))
        # if closest_stone:
        #     pygame.draw.line(self.screen, "BLUE", (self.spaceship.rect.right, self.spaceship.rect.centery),
        #                      (closest_stone.rect.centerx, closest_stone.rect.top))
        # if missile_intersections:
        #     pygame.draw.line(self.screen, "WHITE", (self.spaceship.rect.right, self.spaceship.rect.centery),
        #                      missile_intersections[0])
        # else:
        #     pygame.draw.line(self.screen, "WHITE", (self.spaceship.rect.right, self.spaceship.rect.centery),
        #                      missile_points)
        if bullet_intersections:
            pygame.draw.line(self.screen, "PURPLE", (self.spaceship.rect.right, self.spaceship.rect.centery),
                             bullet_intersections[0])
        else:
            pygame.draw.line(self.screen, "GREEN", (self.spaceship.rect.right, self.spaceship.rect.centery),
                             (800, self.spaceship.rect.centery))
        for e in closest_enemy1s:
            if e:
                pygame.draw.line(self.screen, "YELLOW", (self.spaceship.rect.right, self.spaceship.rect.centery),
                                 (e.rect.centerx, e.rect.centery))
        # fill_image(inputNum=self.inputNum, inputImg=self.inputImage, WIDTH=800, enemies=self.enemy1Sprites,
        #            spaceship=self.spaceship)
        # size = 10
        # draw_neat(surf=self.screen, size=size, inputNum=self.inputNum, inputImg=self.inputImage, xnodePos=self.xnodePos,
        #           ynodePos=self.ynodePos, x=self.width / 2 - 500, y=(self.height) / 2 - 100)
        # draw_text(self.screen, "FUEL ", 18, self.width / 2, self.height - 50)
        draw_text(self.screen, str(self.spaceship.score), 24, self.width - 24, 24)
        # draw_text(self.screen, str(self.spaceship.fuel), 24, self.width - 100, 24)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()

    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(5))

    winner = p.run(GameObject, 40)
    stats.save_genome_fitness()
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'network.txt')
    run(config_path)
    # GameObject(level=1, fps=60)
