import pygame
from geostatBird import make_K
from scipy.signal import convolve2d
from paramBird import *

class Game:
    def __init__(self):
        gameMap = Map(X, Y, WIDTH, HEIGHT)
        gameMap.computeTileMap(ISLANDS)
        gameMap.computeFishMap()

        players = []
        for j in range(NB_PLAYER):
            players.append(PlayerBird(ISLANDS[0][0], ISLANDS[0][1], ENERGY_MAX, COST_MOVE, COST_DIVE, REWARD, VISIBILITY))

        self.gameMap = gameMap
        self.listPlayer = players
        self.over = [False]*len(players)
        self.q = False

    def reset(self):
        gameMap = Map(X, Y, WIDTH, HEIGHT)
        gameMap.computeTileMap(ISLANDS)
        gameMap.computeFishMap()

        players = []
        for j in range(NB_PLAYER):
            players.append(
                PlayerBird(ISLANDS[0][0], ISLANDS[0][1], ENERGY_MAX, COST_MOVE, COST_DIVE, REWARD, VISIBILITY))

        self.gameMap = gameMap
        self.listPlayer = players
        self.over = [False] * len(players)
        self.q = False

    def quit(self):
        self.q = True


class Map:
    '''
    Map :
    - Define Grid Size
    - Put Islands and Water
    - Add Random Fish
    + function to plot it through pygame
    '''

    def __init__(self, x, y, screen_width, screen_height):

        # game characteristics
        self.gridX = x
        self.gridY = y
        self.gridSize = (len(y), len(x))
        self.tileMap = None
        self.fishMap = None

        # useful game dimensions for plotting
        self.mapwidth = len(x)
        self.mapheight = len(y)
        self.tilesize = screen_height / self.mapheight

    def computeTileMap(self, island):
        tilemap = [[WATER for i in range(self.gridSize[1])] for i in range(self.gridSize[0])]

        # place island where wanted
        for pos in island:
            tilemap[pos[0]][pos[1]] = ISLAND
        self.tileMap = tilemap

    def computeFishMap(self):

        h = 10
        lam = 2

        grid = np.array(np.meshgrid(self.gridY, self.gridX)).T.reshape(-1, 2)
        # make a covariance matrix:
        K = make_K(grid, h, lam)
        mean = -h * np.ones(len(grid))
        RF = np.random.multivariate_normal(mean, K)
        RF = RF.reshape(self.gridSize[0], self.gridSize[1])

        self.fishMap = np.round(RF * (RF > 0)) * self.tileMap

    def draw(self, screen):
        screen.blit(pygame.image.load('./graphics/islandsula.png'), (0, 0))

class PlayerBird:
    """
    Bird :
    - Define State (Energy, position, and nbFish/area)
    - Define transition action to state
    + function to plot it through pygame
    """

    def __init__(self, row, col, energyMax, costMove, costDive, reward, visibility):
        self.row = row
        self.col = col
        self.init_pos = (row, col)
        self.energyMax = energyMax
        self.costMove = costMove
        self.costDive = costDive

        # nb of each activity
        self.nbMove = 0
        self.nbDive = 0
        self.nbFish = np.zeros((len(Y), len(X)))
        self.visibility = visibility
        self.reward = reward

    def moveRight(self, gameMap):
        if self.col < max(gameMap.gridX):
            self.col += 1
        self.nbMove += 1

    def moveLeft(self, gameMap):
        if self.col > min(gameMap.gridX):
            self.col -= 1
        self.nbMove += 1

    def moveUp(self, gameMap):
        if self.row > min(gameMap.gridY):
            self.row -= 1
        self.nbMove += 1

    def moveDown(self, gameMap):
        if self.row < max(gameMap.gridY):
            self.row += 1
        self.nbMove += 1

    def moveDive(self, gameMap):
        self.nbDive += 1
        if gameMap.fishMap[self.row][self.col]>0:
            self.nbFish[self.row, self.col] += 1
            gameMap.fishMap[self.row][self.col] -= 1

    def getLife(self):
        energy = self.energyMax + self.nbMove * self.costMove + self.nbDive * self.costDive
        return max(energy, 0)

    def getScore(self):
        dead = (self.getLife() <= 0)
        if dead:
            score = self.reward["lose"]
        else :
            score = np.sum(self.nbFish)*self.reward["win"]
        return score

    def game_over(self):
        dead = (self.getLife() <= 0)
        home = (self.init_pos == (self.row, self.col))
        satiated = (np.sum(self.nbFish) > 0)
        return dead + home*satiated

    def drawPos(self, screen, gameMap, other=False):
        # display the player at the correct position
        if other:
            picture = './graphics/bird_other.png'
        else:
            picture = './graphics/bird.png'

        p = pygame.image.load(picture)
        screen.blit(p, (self.col * gameMap.tilesize, self.row * gameMap.tilesize))

    def drawProperties(self, screen, gameMap):
        # display score's legend
        legend = pygame.image.load('./graphics/fish.png')
        posL = ((gameMap.gridSize[1] + 1) * gameMap.tilesize, 0)
        screen.blit(legend, posL)

        # display score
        font = pygame.font.SysFont("comicsans", 20)
        t = font.render(str(np.sum(self.nbFish)), True, WHITE, BLACK)
        posT = ((gameMap.gridSize[1] + 0.5) * gameMap.tilesize, 0)
        screen.blit(t, posT)

        # display health bar
        # (left, top, width, height)
        pygame.draw.rect(screen, PURPLE, ((gameMap.gridSize[1] + 0.5) * gameMap.tilesize,
                                          1.5 * gameMap.tilesize,
                                          gameMap.tilesize,
                                          (gameMap.gridSize[0] - 2) * gameMap.tilesize))
        pygame.draw.rect(screen, RED, ((gameMap.gridSize[1] + 0.5) * gameMap.tilesize,
                                       1.5 * gameMap.tilesize + (gameMap.gridSize[0] - 2) * gameMap.tilesize * (
                                               1 - self.getLife() / self.energyMax),
                                       gameMap.tilesize,
                                       (gameMap.gridSize[0] - 2) * gameMap.tilesize * self.getLife() / self.energyMax))

        # display health bar's legend
        t = font.render("Energy", True, WHITE, BLACK)
        posT = ((gameMap.gridSize[1] + 0.5) * gameMap.tilesize, 0.9 * gameMap.tilesize)
        screen.blit(t, posT)

        # display If dead
        font = pygame.font.SysFont("comicsans", 40)
        if self.game_over():
            if self.getScore()>0:
                text = "YOU WIN"
            else:
                text = "YOU LOSE"
            t = font.render(text, True, WHITE, BLACK)
            posT = (gameMap.gridSize[1] / 2 * gameMap.tilesize, gameMap.gridSize[1] / 2 * gameMap.tilesize)
            screen.blit(t, posT)

    def drawFish(self, screen, gameMap):
        # display visible Map
        # loop through each row
        for row in range(gameMap.mapheight):
            # loop through each column in the row
            for column in range(gameMap.mapwidth):
                ## Check distance to bird position
                if (abs(self.row - row) <= self.visibility) & (abs(self.col - column) <= self.visibility):
                    ## Plot Fish presence
                    if gameMap.fishMap[row][column] > 0:
                        FISH = pygame.image.load('./graphics/fish.png')
                        screen.blit(FISH, (column * gameMap.tilesize, row * gameMap.tilesize))

    def visible_fish_map(self, gameMap):

        boundaryMap = gameMap.fishMap.copy()
        k = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
        for i in range(self.visibility):
            boundaryMap = convolve2d(boundaryMap, k)

        minrow = self.row
        maxrow = self.row + 2 * self.visibility + 1
        mincol = self.col
        maxcol = self.col + 2 * self.visibility + 1

        visible_fish_map = boundaryMap[minrow:maxrow, mincol:maxcol]
        return visible_fish_map

    def get_states(self, gg):

        visible_fishMap = gg.gameMap.fishMap.copy()
        for row in range(gg.gameMap.mapheight):
            for column in range(gg.gameMap.mapwidth):
                if (abs(self.row - row) > self.visibility) | (abs(self.col - column) > self.visibility):
                    visible_fishMap[row, column] = 0
        print(visible_fishMap)

        visible_players = 0 *  gg.gameMap.fishMap.copy()
        for p in gg.listPlayer:
            visible_players[p.row, p.col] = -1
        visible_players[self.row, self.col] = 1
        print(visible_players)

        print(self.nbFish)
