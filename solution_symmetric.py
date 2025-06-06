from bus import Bus
from circuit import Circuit
from settings import s
from load import Load
import numpy as np
import pandas as pd
from generator import Generator

class Solution_Faults:

    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.voltage_pu = 1.0  # Pre-fault voltage in per-unit
        generators = self.circuit.generators
        
        # Check if circuit has Ybus calculated
        if self.circuit.ybus is None:
            self.circuit.calc_ybus()
        
        # Convert pandas DataFrame to numpy array for calculations
        num_buses = len(self.circuit.buses)
        self.ybus = np.zeros((num_buses, num_buses), dtype=complex)


        # self.ybus[0,0] = self.ybus[0,0] + generators["G1"].y_bus_admittance
        # self.ybus[6,6] = self.ybus[6,6] + generators["G7"].y_bus_admittance
        
        for i in range(num_buses):
            for j in range(num_buses):
                self.ybus[i, j] = self.circuit.ybus.iloc[i, j]

        # Add generator contributions dynamically, not hardcoded
        for gen_name, generator in generators.items():
            if hasattr(generator, 'bus') and hasattr(generator.bus, 'index'):
                bus_idx = generator.bus.index
                if 0 <= bus_idx < num_buses:  # Check index is in bounds
                    if hasattr(generator, 'y_bus_admittance'):
                        self.ybus[bus_idx, bus_idx] += generator.y_bus_admittance
        
        # Calculate Zbus (inverse of Ybus)
        self.zbus = np.linalg.inv(self.ybus)

    # def calculate_fault_currents(self, bus: Bus):
    #     num_buses = len(self.circuit.buses)
    #     # fault_currents = np.zeros(num_buses, dtype=complex)
    #     # bus_voltages_after_fault = np.zeros(num_buses, dtype=complex)
    #     fault_currents = 0
    #     bus_voltages_after_fault = 0

    #     Znn = self.zbus[bus.index, bus.index]

    #     # Calculate fault current at the nth bus (which is now the current bus)
    #     Ifn_prime = self.voltage_pu / Znn
    #     fault_currents[bus.index] = Ifn_prime
        
    #     # Calculate bus voltage after fault for the nth bus
    #     # bus_voltages_after_fault[n] = En

    #     for bus in self.circuit.buses.values():
    #         k = bus.index
    #         Zkk = self.zbus[k, k]
            
    #         # Calculate fault current at the nth bus
    #         # Ifk_prime = self.voltage_pu / Zkk
    #         # fault_currents[k] = Ifk_prime
            
    #         # Calculate bus voltage after fault for the nth bus
    #         Ek = (1 - (self.zbus[k, k] / Zkk)) * self.voltage_pu
    #         bus_voltages_after_fault[k] = Ek

    #     return fault_currents, bus_voltages_after_fault

    def calculate_fault_currents_2(self, bus: Bus):
        """
        Will overwrite calculate_fault_currents if correct
        """
        
        # Get the impedance at the fault bus (Znn)
        Znn = self.zbus[bus.index, bus.index]
        
        # Calculate fault current at the selected bus
        fault_current = self.voltage_pu / Znn
        
        # Calculate bus voltages after fault for all buses
        num_buses = len(self.circuit.buses)
        bus_voltages_after_fault = np.zeros(num_buses, dtype=complex)
        
        for k in range(num_buses):
            # Calculate bus voltage after fault for each bus
            bus_voltages_after_fault[k] = (1 - (self.zbus[k, bus.index] / Znn)) * self.voltage_pu
        
        return fault_current, bus_voltages_after_fault
