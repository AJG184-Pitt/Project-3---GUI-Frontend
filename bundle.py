import math

class Bundle:
    def __init__(self, name, num_conductors, spacing, conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor
        self.DSC, self.DSL = self.calc_radii()

    def calc_radii(self):
        if self.num_conductor == 1:
            self.DSC = 0
        else:
            self.DSC = self.spacing

        self.DSL = self.spacing / (2 * math.sin(math.pi/self.num_conductors))
        return self.DSC, self.DSL
