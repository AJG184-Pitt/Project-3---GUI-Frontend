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

    def calc_Deq(self):