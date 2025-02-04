class Transformer:
    def __init__(self, name, bus1, bus2, power_rating, impedance_percent, x_over_r_ratio):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.power_rating = power_rating
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio
        self.zt = self.calc_impedance()
        self.yt = self.calc_admittance()
        self.yprim = None

        def calc_impedance(self):
            theta = np.atan(x_over_r_ratio)
            zpu = self.impedance_percent/100
            xpu = zpu/ np.sin(theta)
            rpu = zpu / np.cos(theta)
            return self.zt

        def calc_admittance(self):
            if self.zt != 0:
                return 1 / self.zt
            else:
                return 0
