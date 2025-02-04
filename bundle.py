class Bundle:
    def __init__(self, name, num_conductors, spacing, conductor):
        self.name = name
        self.num_conductors = num_conductors
        self.spacing = spacing
        self.conductor = conductor
        self.DSC, self.DSL = self.calc_radii()

    def calc_radii(self):
