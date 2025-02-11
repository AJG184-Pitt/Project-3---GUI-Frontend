class Conductor:
    def __init__(self, name: str, diam: float, GMR: float, resistance: float, ampacity: float):
        self.name = name
        self.diam = diam
        self.radius = diam / 24 # diameter is in inches and radius needs to be in feet
        self.GMR = GMR
        self.resistance = resistance
        self.ampacity = ampacity
