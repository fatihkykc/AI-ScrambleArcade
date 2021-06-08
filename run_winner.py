import os

import main
import GAMEOBJECT
import neat
import pickle


def replay_genome(config_path, genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    GAMEOBJECT.GameObject(genomes, config)


local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'network.txt')
replay_genome(config_path)

# winner1.pkl 13 inp 1 hid 6 out
