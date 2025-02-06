import numpy as np
class TransmissionLine:
    def __init__(self, name, bus1, bus2, bundle, conductor, geometry, length,f):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.bundle = bundle
        self.conductor = conductor
        self.geometry = geometry
        self.length = length
        self.f = 60
        self.rseries, self.xseries, self.bseries, self.yseries = self.calc_series()


    def calc_series(self):
        self.rseries = self.conductor.resistance_c/self.conductor.num_conductors
        self.xseries = (2 * np.pi * self.f) * (2 * 10 ** -7) * np.log(self.geometry.Deq/self.bundle.DSL) * 1609.34
        self.bseries = (2 * np.pi * self.f) * ((2 * np.pi * 8.854 * 10 ** -12)/(np.log(self.geometry.Deq/self.bundle.DSC))) * 1609.34
        self.yseries = 1 / (self.rseries + (1j * self.xseries))