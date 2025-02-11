import numpy as np

class Transformer:
    def __init__(self, name: str, bus1: str, bus2: str, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.xpu = float
        self.rpu = float
        self.theta = float
        # per unit calc will need to change to impedence eventually
        self.zpu = self.calc_impedance()
        self.yt = self.calc_admittance()
        self.yprim = None

    def calc_impedance(self):
        self.theta = np.atan(self.x_over_r_ratio)
        self.zpu = self.impedance_percent/100
        self.xpu = self.zpu/ np.sin(self.theta)
        self.rpu = self.zpu / np.cos(self.theta)
        return self.zpu

    def calc_admittance(self):
        if self.zpu != 0:
            return 1/self.zpu
        else:
            return 0
