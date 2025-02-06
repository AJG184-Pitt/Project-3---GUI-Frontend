class Conductor:
    def __init__(self, name, diam, GMR, resistance, ampacity):
        self.name = name
        self.diam = diam
        self.radius = diam / 24
        self.GMR = GMR
        self.resistance = resistance
        # self.resistance_c = float
        self.ampacity = ampacity
