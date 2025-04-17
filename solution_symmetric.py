from bus import Bus
from circuit import Circuit
from settings import s
from load import Load
import numpy as np
import pandas as pd

class Solution_Faults:

    def __init__(self, circuit):
        self.circuit = circuit
        self.voltage_pu = 1.0  # Pre-fault voltage in per-unit

        # Initialize admittance matrix (Ybus) and impedance matrix (Zbus)
        num_buses = len(self.circuit.buses)
        self.ybus = np.zeros((num_buses, num_buses), dtype=complex)

        # Populate Ybus with shunt elements from buses
        for bus in self.circuit.buses.values():
            if hasattr(bus, 'shunt_admittance'):
                self.ybus[bus.index, bus.index] += bus.shunt_admittance

        # Add branch admittances to Ybus
        for branch in self.circuit.branches.values():
            y = 1 / (branch.impedance * complex(1, -branch.x_r_ratio))
            if hasattr(branch.bus1, 'index') and hasattr(branch.bus2, 'index'):
                i1 = branch.bus1.index
                i2 = branch.bus2.index
                self.ybus[i1, i1] += y
                self.ybus[i2, i2] += y
                self.ybus[i1, i2] -= y
                self.ybus[i2, i1] -= y

        # Calculate Zbus (inverse of Ybus)
        self.zbus = np.linalg.inv(self.ybus)

    def calculate_fault_currents(self):
        num_buses = len(self.circuit.buses)
        fault_currents = np.zeros(num_buses, dtype=complex)
        bus_voltages_after_fault = np.zeros(num_buses, dtype=complex)

        for bus in self.circuit.buses.values():
            if hasattr(bus, 'index'):
                n = bus.index
                Znn = self.zbus[n, n]
                
                # Calculate fault current at the nth bus
                Ifn_prime = self.voltage_pu / Znn
                fault_currents[n] = Ifn_prime
                
                # Calculate bus voltage after fault for the nth bus
                Ek = 1 - (self.zbus[n, n] / Znn) * self.voltage_pu
                bus_voltages_after_fault[n] = Ek

        return fault_currents, bus_voltages_after_fault
