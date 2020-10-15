import numpy as np
import matplotlib.pyplot as plt

def cov_kernel(a, b, h, lam):
    """
    Squared-Exponential covariance kernel
    """
    k12 = h ** 2 * np.exp(-1. * np.sum((a - b) ** 2) / lam ** 2)
    return k12


def make_K(grid, h, lam):
    """
    Make covariance matrix from covariance kernel
    """
    # for a data array of length x, make a covariance matrix x*x:
    K = np.zeros((len(grid), len(grid)))

    for i in range(0, len(grid)):
        for j in range(0, len(grid)):
            # calculate value of K for each separation:
            K[i, j] = cov_kernel(grid[i,:], grid[j,:], h, lam)

    return K


# # make an array of 200 evenly spaced positions between 0 and 20:
# x = np.arange(0, 20)
# y = np.arange(0, 10)
# grid = np.array(np.meshgrid(x, y)).T.reshape(-1, 2)
#
# # make a covariance matrix:
# K = make_K(grid, h = 10, lam = 2)
#
# # draw samples from a co-variate Gaussian
# # distribution, N(0,K), at positions x1:
# mean = -10 * np.ones(len(grid))
# RF = np.random.multivariate_normal(mean, K)
#
# print(RF.shape)
# RF = RF.reshape(len(x), len(y))
# RF = np.round(RF * (RF > 0))
#
#
# plt.imshow(RF);
# plt.colorbar()
# plt.show()
