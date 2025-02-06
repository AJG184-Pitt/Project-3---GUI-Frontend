import numpy as np

class Bundle:
    def __init__(self, name, num_conductors, spacing, conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor
        self.DSC, self.DSL = self.calc_radii()

    def calc_radii(self):
        if self.num_conductors == 1:
            self.DSC = self.conductor.radius
            self.DSL = self.conductor.GMR
        elif self.num_conductors == 2:
            self.DSC = np.sqrt(self.conductor.radius * self.spacing)
            self.DSL = np.sqrt(self.conductor.GMR * self.spacing)
        elif self.num_conductors == 3:
            self.DSC = np.cbrt(self.conductor.radius * self.spacing**2)
            self.DSL = np.cbrt(self.conductor.GMR * self.spacing**2)
        elif self.num_conductors == 4:
            self.DSC = 1.091 * np.power(self.conductor.radius * self.spacing**4, 1/4)
            self.DSL = 1.091 * np.power(self.conductor.GMR * self.spacing**4, 1/4)
        else:
            print("Invalid conductors for a bundle")
