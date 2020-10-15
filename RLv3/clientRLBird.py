import pygame
import numpy as np
from networkBird import Network
from paramBird import WIDTH, HEIGHT
import time
import imageio

def redrawWindow(win, gg, p):
    gg.gameMap.draw(win)
    gg.listPlayer[p].drawProperties(win, gg.gameMap)
    gg.listPlayer[p].drawFish(win, gg.gameMap)

    for pl in gg.listPlayer:
        pl.drawPos(win, gg.gameMap, True)
    gg.listPlayer[p].drawPos(win, gg.gameMap)
    pygame.display.update()

def client(seed):

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Client")
    pygame.font.init()

    n = Network()
    player = int(n.getP())
    print("You are player", player)

    np.random.seed(seed)

    run = True
    clock = pygame.time.Clock()
    images = []
    dt = 0
    while run:
        clock.tick(60)
        try:
            # Get Game
            gg = n.send("get")
            redrawWindow(win, gg, player)
            pic = './results/screenshot_player' + str(player) + '_step' + str(dt) + '.jpeg'
            pygame.image.save(win, pic)
            images.append(imageio.imread(pic))
            dt += 1
        except:
            run = False
            print("Couldn't get game")
            break

        if not gg.listPlayer[player].game_over():
            # time.sleep(1)
            move = np.random.choice(["left", "right", "down", "up", "dive"])
            n.send(move)
        else:
            n.send("gameover")
            # print("GAME FINISH")
            # print("Your Score :", gg.listPlayer[player].getScore())

        if gg.q:
            run = False

    imageio.mimsave('./results/RL_Bird_player' + str(player) + '.gif', images)
    pygame.quit()


# client()
