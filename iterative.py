import sys

from main import *
import neat

screen_width = 1500
screen_height = 800
generation = 0


def run_spaceship(genomes, config):
    # Init NEAT
    nets = []
    spaceships = []
    # sprite groups
    space = Space()
    rocketSprites = pygame.sprite.Group()
    shootSprites = pygame.sprite.Group()
    systemSprites = pygame.sprite.Group(space)
    userSprites = pygame.sprite.Group()
    enemySprites = pygame.sprite.Group()
    fuelSprites = pygame.sprite.Group()

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Init my spaceships
        spaceship = SpaceShip(shootSprites)
        spaceships.append(spaceship)
        userSprites.add(spaceship)

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)

    # Main loop
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Input my data and get result from network
        for index, spaceship in enumerate(spaceships):
            output = nets[index].activate(
                # spaceship.get_distance(ground),
                # spaceship.get_distance(top),
                spaceship.get_distance(enemy),
                spaceship.get_distance(enemyrocket),
                spaceship.get_distance(fuel))
            )
            i = output.index(max(output))
            if i == 0:
                spaceship.shoot()
            elif i == 1:
                spaceship.missile()
            elif i == 2:
                spaceship.move_up()
            elif i == 3:
                spaceship.move_down()
            elif i == 4:
                spaceship.move_right()
            elif i == 4:
                spaceship.move_left()

            # Update spaceship and fitness
            remain_spaceships = 0
            for i, spaceship in enumerate(spaceships):
                if
            (spaceship.get_alive()):
            remain_spaceships += 1
            spaceship.update(map)
            genomes[i][1].fitness += spaceship.get_reward()

            # check
            if remain_spaceships == 0:
                break

        # Drawing
        screen.blit(map, (0, 0))
        for spaceship in spaceships:
            if spaceship.get_alive():
                spaceship.draw(screen)

        text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width / 2, 100)
        screen.blit(text, text_rect)

        text = font.render("remain spaceships : " + str(remain_spaceships), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width / 2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)


if __name__ == "__main__":
    # Set configuration file
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_spaceship, 1000)
