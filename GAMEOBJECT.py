from main import *


class GameObject:
    """Oyun objesi."""

    def __init__(self, height=640, width=800, keepgoing=True, level=1, game_over=False, fps=60):
        pygame.init()
        self.white = (255, 255, 255)
        pygame.mixer.init()
        self.currentLevel = level
        self.fps = fps
        self.width = width
        self.height = height
        self.keepgoing = keepgoing
        self.game_over = game_over
        self.initScreen()
        self.fillBackground()
        self.blit()
        self.lives = [Lives(1), Lives(2), Lives(3)]
        self.initSprites()
        self.load_data()
        self.update()

    def update(self):
        """Update fonksiyonu her frame de çağrılır."""
        while self.spaceship.lives >= 0:
            if self.spaceship.lives == 0:
                self.game_over = True
            self.keepGoing()
            self.colliders()
            self.spriteUpdate()
            self.clear()
            self.draw()
            self.isThisTheEnd()
            pygame.display.flip()

    def isThisTheEnd(self):
        """Oyun sonu"""
        if self.theEndGame.end():
            try:
                self.level()
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
                    self.enemySprites.add(self.enemy3)
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

        # bullet-enemy collider
        bullethits = pygame.sprite.groupcollide(self.enemySprites, self.shootSprites, True, True)
        for hit in bullethits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if bullethits:
            self.spaceship.score += 1

        # player-enemy collider
        spaceshiphits = pygame.sprite.spritecollide(self.spaceship, self.enemySprites, True)
        for hit in spaceshiphits:
            expl = Explosion(hit.rect.center, 'sm')
            self.explosionSprites.add(expl)
        if spaceshiphits:
            self.spaceship.score -= 5
            self.spaceship.lives -= 1
            self.lives[-1].kill()
            del self.lives[-1]

        # spaceship-ground collider
        spaceshiphitsground = pygame.sprite.spritecollide(self.spaceship, self.stoneSprites, False)
        if spaceshiphitsground:
            self.spaceship.lives = 0

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
        self.enemySprites = pygame.sprite.Group()
        self.fuelSprites = pygame.sprite.Group()
        self.shootSprites = pygame.sprite.Group()
        self.stoneSprites = pygame.sprite.Group()
        self.spaceship = SpaceShip(self.shootSprites, self.width, self.height)
        self.userSprites = pygame.sprite.Group(self.spaceship)
        self.rocket = Rockets(self.spaceship.rect.right, self.spaceship.rect.center[1], self.spaceship.rangey)

    def keepGoing(self, isWave1=False, isWave2=False):
        """1. ve 2. düşman dalgalarını ve oyun bitiş, açılış ekranını kontrol eder."""
        self.isWave1 = isWave1
        self.isWave2 = isWave2
        if self.keepgoing:
            self.show_strt_screen()
            self.keepgoing = False
            self.lives = [Lives(1), Lives(2), Lives(3)]
            self.initSprites()
            self.level()

        if self.game_over:
            self.show_go_screen()
            self.game_over = False
            self.lives = [Lives(1), Lives(2), Lives(3)]
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
            for i in range(50):
                self.enemy = Enemy1()
                self.enemy.rect.x = random.randrange(600, 8064)
                self.enemy.rect.y = random.randrange(0, self.height // 2 + 50)
                self.enemySprites.add(self.enemy)
        if self.currentLevel == 2 or self.currentLevel == 3:
            for i in range(50):
                self.enemy2 = Enemy2()
                self.enemy2.rect.x = random.randrange(600, 8064)
                self.enemy2.rect.y = random.randrange(0, self.height // 2 + 50)
                self.enemySprites.add(self.enemy2)

    def clear(self):
        """ekranı temizler."""
        self.systemSprites.clear(self.screen, self.background)
        self.userSprites.clear(self.screen, self.background)
        self.stoneSprites.clear(self.screen, self.background)
        self.enemySprites.clear(self.screen, self.background)
        self.fuelSprites.clear(self.screen, self.background)
        self.shootSprites.clear(self.screen, self.background)
        self.explosionSprites.clear(self.screen, self.background)
        self.liveSprites.clear(self.screen, self.background)

    def spriteUpdate(self):
        """bütün spriteların update fonksiyonlarını çalıştırır."""
        self.systemSprites.update()
        self.userSprites.update()
        self.stoneSprites.update()
        self.enemySprites.update()
        self.fuelSprites.update()
        self.shootSprites.update()
        self.explosionSprites.update()
        self.liveSprites.update()

    def draw(self):
        """bütün spriteları ekrana çizer"""
        self.systemSprites.draw(self.screen)
        self.userSprites.draw(self.screen)
        self.stoneSprites.draw(self.screen)
        self.enemySprites.draw(self.screen)
        self.fuelSprites.draw(self.screen)
        self.shootSprites.draw(self.screen)
        self.explosionSprites.draw(self.screen)
        self.liveSprites.draw(self.screen)
        self.draw_player_fuel(self.screen, self.width / 2 - 100, self.height - 50, self.spaceship.fuel / 100)
        draw_text(self.screen, "FUEL ", 18, self.width / 2, self.height - 50)
        draw_text(self.screen, str(self.spaceship.score), 24, self.width - 24, 24)
        draw_text(self.screen, str(self.spaceship.fuel), 24, self.width - 100, 24)


if __name__ == '__main__':
    # local_dir = os.path.dirname(__file__)
    # config_path = os.path.join(local_dir, 'network.txt')
    # run(config_path)
    GameObject(level=1, fps=60)
