import numpy as np
from bus import Bus

class Transformer:
    def __init__(self, name: str, bus1: Bus, bus2: Bus, power_rating: float, impedance_percent: float, x_over_r_ratio: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.xpu = float
        self.rpu = float
        # per unit calc will need to change to impedence eventually
        self.zpu = self.calc_impedance()
        self.yt = self.calc_admittance()
        self.yprim = None

    def calc_impedance(self):
        theta = np.atan(self.x_over_r_ratio)
        zmag = self.impedance_percent/100
        self.xpu = zmag/ np.sin(theta)
        self.rpu = zmag / np.cos(theta)
        return self.rpu + 1j * self.xpu

    def calc_admittance(self):
        if self.zpu != 0:
            return 1/self.zpu
        else:
            return 0
