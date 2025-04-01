import numpy as np
from enum import Enum

class BusType:
    SLACK = 1
    PV = 2
    PQ = 3

class Jacobian:
    def __init__(self):
        pass

    def calc_jacobian(self, buses, ybus, angles, voltages):
        """
        Calculate 
        """