class Conductor:
    def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        self.name = name
        self.diam = diam
        self.radius = diam / 24
        self.GMR = GMR
        self.resistance = resistance
        # self.resistance_c = float
        self.ampacity = ampacity
