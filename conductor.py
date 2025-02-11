class Conductor:
    def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        self.name = name
        self.diam = diam
        self.radius = diam / 24 # Need to convert feet to inches (12*2 = 24)
        self.GMR = GMR
        self.resistance = resistance
        self.ampacity = ampacity
