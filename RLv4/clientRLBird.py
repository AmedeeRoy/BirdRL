import pygame
import numpy as np
from networkBird import Network
from paramBird import WIDTH, HEIGHT
import time

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
    while run:
        clock.tick(60)
        try:
            # Get Game
            gg = n.send("get")
            redrawWindow(win, gg, player)
        except:
            run = False
            print("Couldn't get game")
            break

        if not gg.listPlayer[player].game_over():
            gg.listPlayer[player].get_states(gg)

            time.sleep(1)
            move = np.random.choice(["left", "right", "down", "up", "dive"])
            n.send(move)

        else:
            n.send("gameover")
            # print("GAME FINISH")
            # print("Your Score :", gg.listPlayer[player].getScore())

        if gg.q:
            run = False

    pygame.quit()


client(0)
