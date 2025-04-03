from bus import Bus
from circuit import Circuit
import numpy as np
import pandas as pd

class Solution:

    def __init__(self, name: str, bus_k: Bus, bus_j: Bus, circuit: Circuit):
        self.name = name
        self.bus1 = bus_k
        self.bus2 = bus_j
        self.circuit = Circuit
        self.delta = dict()
        self.voltage = dict()
        self.P = self.calc_Px()
        self.Q = self.calc_Qx()

    def start(self):
        self.delta = {bus: 0 for bus in self.Bus.bus_count}
        self.voltages = {bus: 1 for bus in self.Bus.bus_count}


    def calc_Px(self):
        Px = {bus: 0 for bus in self.Bus.bus_count}

        for k, bus_k in enumerate(self.Bus.bus_count):
            V_k = self.voltage[bus_k]
            delta_k = self.delta[bus_k]
            P_k = 0
            for j, bus_j in enumerate(self.Bus.bus_count):
                V_j = self.voltage[bus_j]
                delta_j = self.delta[bus_j]
                Y_kj = self.Circuit.ybus[k, j]
                P_k = V_k * V_j * abs(Y_kj) * np.cos(delta_k - delta_j - np.angle(Y_kj))

            Px[bus_k] = P_k

        return Px

    def calc_Qx(self):
        Qx = {bus: 0 for bus in self.Bus.bus_count}

        for k, bus_k in enumerate(self.Bus.bus_count):
            V_k = self.voltage[bus_k]
            delta_k = self.delta[bus_k]
            Q_k = 0
            for j, bus_j in enumerate(self.Bus.bus_count):
                V_j = self.voltage[bus_j]
                delta_j = self.delta[bus_j]
                Y_kj = self.Circuit.ybus[k, j]
                Q_k = V_k * V_j * abs(Y_kj) * np.sin(delta_k - delta_j - np.angle(Y_kj))

            Qx[bus_k] = Q_k

        return Qx