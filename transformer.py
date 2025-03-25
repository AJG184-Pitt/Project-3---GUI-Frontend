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
        self.xpu_xfmr = float
        self.rpu_xfmr = float
        self.zpu = self.calc_impedance()
        self.ypu = self.calc_admittance()
        self.yprim = self.calc_matrix()

    def calc_impedance(self):
        self.zpu = self.impedance_percent / 100*self.bus1.s_sys / self.power_rating*np.exp(1j * np.arctan(self.x_over_r_ratio))

        self.rpu = self.zpu.real
        self.xpu = self.zpu.imag

        return self.rpu + 1j * self.xpu

    def calc_admittance(self):
        if self.zpu != 0.0:
            return 1.0 / self.zpu
        else:
            return 0.0 + 0.0j

    def calc_matrix(self):
        self.yprim = np.array([[self.ypu, -1*self.ypu],
                            [-1*self.ypu, self.ypu]])
        return self.yprim

if __name__ == '__main__':
    bus1 = Bus("B1", 180)
    bus2 = Bus("B2", 230)

    transformer1 = Transformer("T1", bus1, bus2, 125, 8.5, 10)

    print(
        f"{transformer1.name} {transformer1.bus1}, {transformer1.bus2}, {transformer1.power_rating}, {transformer1.impedance_percent}, {transformer1.x_over_r_ratio}")
    print(transformer1.calc_admittance())
    print(transformer1.calc_impedance())
    print(transformer1.calc_matrix())
