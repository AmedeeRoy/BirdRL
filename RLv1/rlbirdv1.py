import pygame
from pygame.constants import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_d, K_s, QUIT, KEYDOWN
from ple.games import base
import numpy as np
import sys
from math import factorial as fac

# constants representing the different resources
ISLAND  = 0
WATER = 1

# constants representing plotting colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PURPLE = (50, 50, 50)

class Map(pygame.sprite.Sprite):
    '''
    Map :
    - Define Grid Size
    - Put Islands and Water
    - Add Random Fish
    + function to plot it through pygame
    '''
    def __init__(self, x, y, screen_width, screen_height):

        # init as pygame class
        pygame.sprite.Sprite.__init__(self)

        # game characteristics
        self.gridX = x
        self.gridY = y
        self.gridSize = (len(y), len(x))
        self.tileMap = None
        self.fishMap = None
        # useful game dimensions for plotting
        self.mapwidth = len(x)
        self.mapheight = len(y)
        self.tilesize  = screen_height/self.mapheight

    def computeTileMap(self, island):
        tilemap = [[WATER for i in range(self.gridSize[1])] for i in range(self.gridSize[0])]
        # place island where wanted
        for pos in island:
            tilemap[pos[0]][pos[1]] = ISLAND
        self.tileMap = tilemap

    def computeFishMap(self):
        # Random Fish
        self.fishMap = np.array(self.tileMap) * np.random.random(self.gridSize)

        # add Geometry Filter
        self.fishMap *= np.array([[np.sqrt(i**2 + j**2) for i in range(self.gridSize[1])] \
                      for j in range(self.gridSize[0])])/np.sqrt(self.gridSize[0]**2+self.gridSize[1]**2)


    def draw(self, screen):
        # a dictionary linking resources to colours
        map_3x3 = pygame.image.load('./graphics/map_3x3.png')
        screen.blit(map_3x3,(0,0))

class Bird(pygame.sprite.Sprite):
    '''
    Bird :
    - Define State (Energy, position, and nbFish/area)
    - Define transition action to state
    + function to plot it through pygame
    '''
    def __init__(self, pos, energyMax, catchMax, costMove, costDive, Map):
        self.position = np.array(pos)
        self.nbStay = 0
        self.nbMove = 0
        self.nbDive = 0
        self.nbFish = 0
        self.catch = False
        self.energyMax = energyMax
        self.catchMax = catchMax
        self.costMove = costMove
        self.costDive = costDive
        self.catchMap = np.zeros(Map.gridSize)
        self.mass = 1000


    def getNbStep(self):
        return self.nbStay + self.nbMove + self.nbDive

    def getLife(self):
        energy = self.energyMax + self.nbMove*self.costMove + self.nbDive*self.costDive
        return max(energy, 0)

    def moveRight(self, Map):
        if self.position[1] < max(Map.gridX):
            self.position[1] += 1
        self.nbMove += 1
    def moveLeft(self, Map):
        if self.position[1] > min(Map.gridX):
            self.position[1] -= 1
        self.nbMove += 1
    def moveUp(self, Map):
        if self.position[0] > min(Map.gridY):
            self.position[0] -= 1
        self.nbMove += 1
    def moveDown(self, Map):
        if self.position[0] < max(Map.gridY):
            self.position[0] += 1
        self.nbMove += 1
    def stay(self):
        self.nbStay += 1
    def dive(self, Map, factorFishFly):
        self.nbDive += 1
        i = self.position[0]
        j = self.position[1]
        prob = Map.fishMap[i][j]
#         print(prob)
        self.catch = np.random.choice([0,1], p = [1-prob, prob])
        if self.catch:
            if np.sum(self.catchMap) < self.catchMax:
                Map.fishMap[i][j] = prob * factorFishFly
                self.catchMap[i][j] += 1
                self.nbFish += 1

    def draw(self, Map, screen, nbStep):
        #display the player at the correct position
        PLAYER = pygame.image.load('./graphics/bird.png')
        screen.blit(PLAYER,(self.position[1]*Map.tilesize, self.position[0]*Map.tilesize))
        #display score's legend
        LEGEND = pygame.image.load('./graphics/fish.png')
        posLEGEND = ((Map.gridSize[1] + 1)*Map.tilesize, 0)
        screen.blit(LEGEND,posLEGEND)
        #display score
        TITLE = pygame.font.Font('./graphics/FreeSansBold.ttf', 18)
        textObj = TITLE.render(str(self.nbFish), True, WHITE, BLACK)
        posTITLE = ((Map.gridSize[1] + 0.5)*Map.tilesize, 0)
        screen.blit(textObj,posTITLE)
        #display health bar
        #(left, top, width, height)
        pygame.draw.rect(screen, PURPLE, ((Map.gridSize[1] + 0.5)*Map.tilesize, \
                                          1.5*Map.tilesize, \
                                          Map.tilesize, \
                                          (Map.gridSize[0]-2)*Map.tilesize))
        pygame.draw.rect(screen, RED, ((Map.gridSize[1] + 0.5)*Map.tilesize, \
                                       1.5*Map.tilesize+(Map.gridSize[0]-2)*Map.tilesize*(1-self.getLife()/self.energyMax),\
                                       Map.tilesize, \
                                       (Map.gridSize[0]-2)*Map.tilesize*self.getLife()/self.energyMax))
        #display health bar's legend
        textObj = TITLE.render("Energy", True, WHITE, BLACK)
        posTITLE = ((Map.gridSize[1] + 0.5)*Map.tilesize, 0.9*Map.tilesize)
        screen.blit(textObj,posTITLE)

        #display nb of Steps
        t = "Step "+str(int(self.getNbStep()))+"/"+str(nbStep)
        textObj = TITLE.render(t, True, WHITE, BLACK)
        posTITLE = ((Map.gridSize[1] + 0.5)*Map.tilesize, (Map.gridSize[0]-0.5)*Map.tilesize)
        screen.blit(textObj,posTITLE)




class RLBird(base.PyGameWrapper):
    '''
        Game PLE
    '''
    def __init__(self, width, height, x, y, island_position, energyMax, catchMax, costMove, \
                 costDive, factorFishFly, nbStep, init_bird_position, reward):

        # list of possible actions
        self.dictAction =  {
                                "left": K_LEFT,
                                "right": K_RIGHT,
                                "down": K_DOWN,
                                "up": K_UP,
                                "stay": K_s,
                                "dive": K_d
                            }
        self.listAction = ["left", "right", "down", "up", "stay", "dive"]

        # init game as pygame-learning-environment class
        base.PyGameWrapper.__init__(self, width, height, actions= self.dictAction)
        # Drawing specific
        self.width = width
        self.height = height
        # Game specific
        self.x = x
        self.y = y
        self.energyMax = energyMax
        self.catchMax = catchMax
        self.costMove = costMove
        self.costDive = costDive
        self.nbStep = nbStep
        self.factorFishFly = factorFishFly
        self.init_bird_position = init_bird_position
        self.island_position = island_position
        self.reward = reward

    def updateFishMap(self, fishMap):
        self.map.fishMap = fishMap
        self.listStates = ListStates(self.energyMax, len(self.x), len(self.y),\
                                      self.catchMax, fishMap, self.factorFishFly)
    def _handle_player_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                #and the game and close the window
                pygame.quit()
                sys.exit()
            #if a key is pressed
            elif event.type == KEYDOWN:
                # action related to player event
                if (event.key == K_RIGHT):
                    self.bird.moveRight(self.map)
                if (event.key == K_LEFT):
                    self.bird.moveLeft(self.map)
                if (event.key == K_UP):
                    self.bird.moveUp(self.map)
                if (event.key == K_DOWN):
                    self.bird.moveDown(self.map)
                if (event.key == K_d):
                    self.bird.dive(self.map, self.factorFishFly)
                if (event.key == K_s):
                    self.bird.stay()
                # re-initialize catch boolean
                self.bird.catch = False
                # update score

    def draw(self, Map):
        TITLE = pygame.font.Font('./graphics/FreeSansBold.ttf', 18)
        #display Win/Loss
        if (self.game_over()):
            if(self.getScore()>0):
                textObj = TITLE.render("YOU WIN", True, WHITE, BLACK)
            else :
                textObj = TITLE.render("YOU LOSE", True, WHITE, BLACK)
            posTITLE = (Map.gridSize[1]/2*Map.tilesize, Map.gridSize[1]/2 * Map.tilesize)
            self.screen.blit(textObj,posTITLE)

    def init(self):
        # Set Map
        m = Map(self.x, self.y, self.width, self.height)
        m.computeTileMap(self.island_position)
        m.computeFishMap()
        self.map = m
        # Set Bird
        self.bird = Bird(self.init_bird_position, self.energyMax, self.catchMax,\
                         self.costMove, self.costDive, self.map)

        # Compute List of States
        self.listStates = ListStates(self.energyMax, len(self.x), len(self.y),\
                                      self.catchMax, self.map.fishMap, self.factorFishFly)

    def getBirdState(self, visibility):
        """
         List with in order:
             - Energy
             - Lon
             - Lat
             - nbFish
        """

        minrow = max(0, self.position[0]-visibility)
        maxrow = min( np.max(self.y), self.position[0]+visibility)
        mincol = max(0, self.position[1]-visibility)
        maxcol = min( np.max(self.x), self.position[1]+visibility)

        visibleMap = self.map.fishMap[minrow:mawrow, mincol, maxcol]

        state = {'energy' : self.bird.getLife(),
                 'row' : self.bird.position[0],
                 'column' : self.bird.position[1],
                 'nbFish' : self.nbFish,
                 'visibleMap' : visibleMap
                }

        return state

    def getGameState(self):
        """
         List with in order:
             - Energy
             - Lon
             - Lat
             - Captures/Area
        """

        state = [self.bird.getLife(),
                 self.bird.position[0],
                 self.bird.position[1],
                 int(self.listStates.map2idx(self.bird.catchMap))
                ]

        return state

    def getScore(self):
        dead = (self.bird.getLife() <= 0)
        home = (tuple(self.bird.position) == tuple(self.init_bird_position))
        return  self.reward["lose"]*dead + home*self.bird.nbFish*self.reward["win"]

    def game_over(self):
        return (self.bird.getNbStep() == self.nbStep) | (self.bird.getLife() <= 0)

    def step(self, dt):

        # -------------- update game
        self._handle_player_events()

        # -------------- update drawing
        self.map.draw(self.screen)
        self.bird.draw(self.map, self.screen, self.nbStep)
        self.draw(self.map)

    def getTransitionProbabilities(self):
        # Actions
        Aleft = np.zeros((self.listStates.size, self.listStates.size))
        Aright = np.zeros((self.listStates.size, self.listStates.size))
        Adown = np.zeros((self.listStates.size, self.listStates.size))
        Aup = np.zeros((self.listStates.size, self.listStates.size))
        Adive = np.zeros((self.listStates.size, self.listStates.size))

        for i in range(self.listStates.size):
            ## LEFT
            nextState = self.listStates.all.copy()[i,:]
            nextState[2] = max(0, nextState[2]-1)                    # LONGITUDINAL MOVE
            nextState[0] = max(0, nextState[0] + self.bird.costMove) # ENERGY COST
            j = self.listStates.state2idx(nextState)
            Aleft[i,j] = 1

             ## RIGHT
            nextState = self.listStates.all.copy()[i,:]
            nextState[2] = min(np.max(self.x), nextState[2]+1)      # LONGITUDINAL MOVE
            nextState[0] = max(0, nextState[0] + self.bird.costMove) # ENERGY COST
            j = self.listStates.state2idx(nextState)
            Aright[i,j] = 1


            ## DOWN
            nextState = self.listStates.all.copy()[i,:]
            nextState[1] = min(np.max(self.y), nextState[1]+1)      # LATITUDINAL MOVE
            nextState[0] = max(0, nextState[0]+ self.bird.costMove) # ENERGY COST
            j = self.listStates.state2idx(nextState)
            Adown[i,j] = 1

            ## UP
            nextState = self.listStates.all.copy()[i,:]
            nextState[1] = max(0, nextState[1] - 1) # LATITUDINAL MOVE
            nextState[0] = max(0, nextState[0] + self.bird.costMove) # ENERGY COST
            j = self.listStates.state2idx(nextState)
            Aup[i,j] = 1

            ## DIVE
            nextState = self.listStates.all.copy()[i,:]
            nextState[0] = max(0, nextState[0] + self.bird.costDive)

            m = self.listStates.idx2map(nextState[3])
            ix = nextState[1]
            iy = nextState[2]

            # related probability of Fish
            p = self.listStates.proba(nextState)

            if (nextState[0] == 0) | ( np.sum(m) >= self.bird.catchMax):
                ii = self.listStates.state2idx(nextState)
                Adive[i,ii] = 1
            else :
                # miss the fish
                ii = self.listStates.state2idx(nextState)
                Adive[i,ii] = 1-p

                # got the fish
                m[ix, iy] = m[ix, iy]+1
                jj = self.listStates.map2idx(m)
                nextState[3] = jj
                ii = self.listStates.state2idx(nextState)
                Adive[i,ii] = p

        Astay = np.identity(self.listStates.size)

        # Transition Probability
        P = [Aleft, Aright, Adown, Aup, Astay, Adive]
        return P

    def getRewardMatrix(self):
        return np.zeros((self.listStates.size, 6))

    def getTerminalRewardMatrix(self):
        h = []
        for i in range(self.listStates.size):
            s = self.listStates.all.copy()[i,:]
            # Check Dead
            if s[0] == 0:
                h.append(self.reward["lose"])
            # Check Home
            elif (s[1], s[2]) == self.init_bird_position :
                # compute nb of fish
                m = self.listStates.idx2map(s[3])
                h.append(np.sum(m)*self.reward["win"])
            else :
                h.append(0)
        return h


class ListStates:
    def __init__(self, nbE, nbX, nbY, nbF, fish, factorFlyFish):
        self.E = np.arange(nbE+1)

        self.X = np.arange(nbX)
        self.Y = np.arange(nbY)

        self.fish = fish
        self.factorFlyFish = factorFlyFish

        # create all map scenarios
        self.maps = self.getMaps(nbX, nbY, nbF)

        # compute theoretical number of scenarios
        n = np.sum([binomial(nbX*nbY + k-1, k) for k in range(nbF+1)])
        self.F = np.arange(n)

        # get all combination
        self.all = np.array(np.meshgrid(self.E, self.Y, self.X, self.F)).T.reshape(-1,4)
        self.size = len(self.all)


    def state2idx(self, s):
        select = np.prod(self.all == s, axis = 1)
        idx = np.where(select)[0]
        return int(idx)

    def idx2state(self, i):
        return self.all[i,:]

    def getMaps(self, nbX, nbY, nbF):
        # create all map scenarios
        mAll = []
        mNew = []
        for f in range(nbF+1):
            if f == 0:
                # No Fish
                m = np.zeros((nbY,nbX))
                mAll.append(m)
                mNew.append(m)
            else :
                mNew_ = []
                for t in mNew:
                    for i in range(nbY):
                        for j in range(nbX):
                            m = t.copy()
                            m[i,j] += 1
                            # check if m already in list
                            select = (mAll == m)
                            test = np.sum([np.prod(select[i]) for i in range(len(select))])
                            if test == 0:
                                    mAll.append(m)
                                    mNew_.append(m)
                mNew = mNew_.copy()
        return mAll

    def idx2map(self, i):
        return self.maps[i].copy()

    def map2idx(self, m):
        select = (self.maps == m)
        idx = np.where([np.prod(select[i]) for i in range(len(self.maps))])[0]
        return int(idx)

    def proba(self, s):
        # initial proba position
        ix = s[1]
        iy = s[2]
        p = self.fish[ix, iy]

        # nb of fishes already captured at this position
        m = self.idx2map(s[3])
        nb = m[ix, iy]

        return p*(self.factorFlyFish)**nb

def binomial(x, y):
    try:
        binom = fac(x) // fac(y) // fac(x - y)
    except ValueError:
        binom = 0
    return binom
