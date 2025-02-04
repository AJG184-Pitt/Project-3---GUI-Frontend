class TransmissionLine:
    def __init__(self, name, bus1, bus2, bundle, geometry, length):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.geometry = geometry
        self.length = length
        self.zseries, self.yshunt = self.calc_admittances()

    def calc_admittances(self):
        return
