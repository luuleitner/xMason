import numpy as np


def meanSD_curves(data):
    Zmn = np.mean(data[: ,6 , :], axis=1)
    Zsd = np.std(data[: ,6 , :], axis=1)
    return Zmn, Zsd