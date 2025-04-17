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
        
        # Check if circuit has Ybus calculated
        if self.circuit.ybus is None:
            self.circuit.calc_ybus()
        
        # Convert pandas DataFrame to numpy array for calculations
        num_buses = len(self.circuit.buses)
        self.ybus = np.zeros((num_buses, num_buses), dtype=complex)
        
        for i in range(num_buses):
            for j in range(num_buses):
                self.ybus[i, j] = self.circuit.ybus.iloc[i, j]
        
        # Calculate Zbus (inverse of Ybus)
        self.zbus = np.linalg.inv(self.ybus)

    def calculate_fault_currents(self):
        num_buses = len(self.circuit.buses)
        fault_currents = np.zeros(num_buses, dtype=complex)
        bus_voltages_after_fault = np.zeros(num_buses, dtype=complex)

        for bus in self.circuit.buses.values():
            n = bus.index
            Znn = self.zbus[n, n]
            
            # Calculate fault current at the nth bus
            Ifn_prime = self.voltage_pu / Znn
            fault_currents[n] = Ifn_prime
            
            # Calculate bus voltage after fault for the nth bus
            Ek = 1 - (self.zbus[n, n] / Znn) * self.voltage_pu
            bus_voltages_after_fault[n] = Ek

        return fault_currents, bus_voltages_after_fault
