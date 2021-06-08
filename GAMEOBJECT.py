import pickle

from main import *
import neat


class GameObject:
    """Oyun objesi."""

    def __init__(self, genomes, config, height=640, width=800, keepgoing=True, level=1, game_over=False, fps=99999):
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
        self.initScreen()
        self.fillBackground()
        self.blit()
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
                    closest_rocket = get_closest(self.spaceship, self.enemy3Sprites)
                    closest_fuel = get_closest(self.spaceship, self.fuelSprites)
                    closest_enemy1s = get_closest_n(self.spaceship, self.enemy1Sprites, 3)
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
                    output = net \
                        .activate(
                        (
                            self.spaceship.rect.right, self.spaceship.rect.centery,
                            *[ce.rect.left if ce else 0 for ce in closest_enemy1s],
                            *[ce.rect.top if ce else 0 for ce in closest_enemy1s],
                            [closest_fuel.rect.left if closest_fuel else 0][0],
                            [closest_fuel.rect.top if closest_fuel else 0][0],
                            [closest_rocket.rect.left if closest_rocket else 0][0],
                            [closest_rocket.rect.top if closest_rocket else 0][0],

                            # self.spaceship.fuel,
                        ))
                    # print(get_coinformation(self.spaceship, self.enemySprites)[:2])
                    self.spaceship.play(output)
                    genome.fitness = self.spaceship.score
                    self.clear()
                    self.draw()
                    self.isThisTheEnd()
                    self.nets.append(net)
                    self.ge.append(genome)
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
        y = 0
        level1 = []
        world = []
        level = open('levels/level' + str(self.currentLevel))
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

        # player-enemy collider
        spaceshiphits = pygame.sprite.spritecollide(self.spaceship, self.enemy3Sprites, True)
        for hit in spaceshiphits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if spaceshiphits:
            self.spaceship.score -= 50
            self.spaceship.lives -= 1
            self.lives[-1].kill()
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
        self.enemy3Sprites = pygame.sprite.Group()
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
            for i in range(75):
                self.enemy = Enemy1()
                self.enemy.rect.x = random.randrange(600, 8064, 10)
                self.enemy.rect.y = random.randrange(30, self.height, 10)
                # self.enemySprites.add(self.enemy)
                self.enemy1Sprites.add(self.enemy)
        if self.currentLevel == 2 or self.currentLevel == 3:
            for i in range(50):
                self.enemy2 = Enemy2()
                self.enemy2.rect.x = random.randrange(600, 8064)
                self.enemy2.rect.y = random.randrange(0, self.height // 2 + 50)
                self.enemySprites.add(self.enemy2)

    # def restart(self):
    #     self.

    def clear(self):
        """ekranı temizler."""
        self.systemSprites.clear(self.screen, self.background)
        self.userSprites.clear(self.screen, self.background)
        self.stoneSprites.clear(self.screen, self.background)
        # self.enemySprites.clear(self.screen, self.background)
        self.enemy1Sprites.clear(self.screen, self.background)
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
        # self.enemySprites.update()
        self.enemy1Sprites.update()
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
        # self.enemySprites.draw(self.screen)
        self.enemy1Sprites.draw(self.screen)
        self.enemy3Sprites.draw(self.screen)
        self.fuelSprites.draw(self.screen)
        self.shootSprites.draw(self.screen)
        self.explosionSprites.draw(self.screen)
        self.liveSprites.draw(self.screen)
        self.draw_player_fuel(self.screen, self.width / 2 - 100, self.height - 50, self.spaceship.fuel / 100)
        closest_rocket = get_closest(self.spaceship, self.enemy3Sprites)
        closest_fuel = get_closest(self.spaceship, self.fuelSprites)
        closest_stone = get_closest(self.spaceship, self.stoneSprites)
        closest_enemy1s = get_closest_n(self.spaceship, self.enemy1Sprites, 3)
        if closest_rocket:
            pygame.draw.line(self.screen, "RED", (self.spaceship.rect.right, self.spaceship.rect.centery),
                             (closest_rocket.rect.centerx, closest_rocket.rect.top))
        if closest_fuel:
            pygame.draw.line(self.screen, "GREEN", (self.spaceship.rect.right, self.spaceship.rect.centery),
                             (closest_fuel.rect.centerx, closest_fuel.rect.top))
        if closest_stone:
            pygame.draw.line(self.screen, "BLUE", (self.spaceship.rect.right, self.spaceship.rect.centery),
                             (closest_stone.rect.centerx, closest_stone.rect.top))

        for e in closest_enemy1s:
            if e:
                pygame.draw.line(self.screen, "YELLOW", (self.spaceship.rect.right, self.spaceship.rect.centery),
                                 (e.rect.centerx, e.rect.top))
        draw_text(self.screen, "FUEL ", 18, self.width / 2, self.height - 50)
        draw_text(self.screen, str(self.spaceship.score), 24, self.width - 24, 24)
        draw_text(self.screen, str(self.spaceship.fuel), 24, self.width - 100, 24)


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
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

    # Run for up to 50 generations.
    winner = p.run(GameObject, 30)
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
