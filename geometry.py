import numpy as np

class Geometry:
    def __init__(self, name, xa, ya, xb, yb, xc, yc):
        self.name = name
        self.xa = xa
        self.ya = ya
        self.xb = xb
        self.yb = yb
        self.xc = xc
        self.yc = yc
        self.Deq = self.calc_Deq()

    # Source: https://www.cuemath.com/distance-formula/

    def calc_Deq(self):
        dab = np.sqrt((self.xb**2 - self.xa**2) + (self.yb**2 - self.ya**2))
        dbc = np.sqrt((self.xc**2 - self.xb**2) + (self.yc**2 - self.yb**2))
        dac = np.sqrt((self.xc**2 - self.xa**2) + (self.yc**2 - self.ya**2))

        return (dab + dbc + dac) / 3
