from gameBird import Game
import numpy as np
from scipy.signal import convolve2d

gg = Game()
print(gg.gameMap.fishMap)

boundaryMap = gg.gameMap.fishMap.copy()
k = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
for i in range(2):
    boundaryMap = convolve2d(boundaryMap, k)

print(boundaryMap)

minrow = gg.listPlayer[0].row
maxrow = gg.listPlayer[0].row + 2 * 2 + 1
mincol = gg.listPlayer[0].col
maxcol = gg.listPlayer[0].col + 2 * 2 + 1

print( 'pos', gg.listPlayer[0].row, gg.listPlayer[0].col)

print('row', minrow, maxrow)

print('col', mincol, maxcol)
visibleMap = boundaryMap[minrow:maxrow, mincol:maxcol]

print(visibleMap)