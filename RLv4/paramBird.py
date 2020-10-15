import numpy as np

# START GAME
X = np.arange(10)
Y = np.arange(10)
ENERGY_MAX = 25
COST_MOVE = -2
COST_DIVE = -3
ISLANDS = [(1, 1)]
VISIBILITY = 1
tile_size = 40
WIDTH = tile_size * (len(X) + 3)
HEIGHT = tile_size * len(Y)
REWARD = {'win': 1000,
          'lose': -1000}
NB_PLAYER = 3
NB_GAMES = 10

# constants representing the different resources
ISLAND = 0
WATER = 1

# constants representing plotting colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PURPLE = (50, 50, 50)


