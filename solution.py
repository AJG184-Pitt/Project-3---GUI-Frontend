from bus import Bus
from circuit import Circuit
from settings import s
from load import Load
import numpy as np
import pandas as pd

class Solution:

    def __init__(self, name: str, bus: Bus, circuit: Circuit, load: Load):
        self.name = name
        self.bus = bus
        self.circuit = circuit
        self.load = load
        self.delta = dict()  # Will be populated with {bus_name: angle_value}
        self.voltage = dict()  # Will be populated with {bus_name: voltage_value}
        # These should be called after delta and voltage are set
        # so move them out of __init__
        self.P = None
        self.Q = None
        self.x = None
        self.y = None
        self.mismatch = None

    # Initialize with flat start
    def start(self):
        self.delta = {bus: 0 for bus in self.bus.index}
        self.voltage = {bus: 1 for bus in self.bus.index}  # Fixed from self.voltages to self.voltage
        # Now calculate the power values
        self.P = self.calc_Px()
        self.Q = self.calc_Qx()
        self.x = self.initialize_x()
        self.y = self.initialize_y()
        self.mismatch = self.calc_mismatch()

    def calc_Px(self):
        # Active power calculation
        Px = {bus: 0 for bus in self.bus.index}

        for k, bus_k in enumerate(self.bus.index):
            V_k = self.voltage[bus_k]
            delta_k = self.delta[bus_k]
            P_k = 0  # Initialize power for this bus
            
            for j, bus_j in enumerate(self.bus.index):
                V_j = self.voltage[bus_j]
                delta_j = self.delta[bus_j]
                Y_kj = self.circuit.ybus.iloc[k, j] if isinstance(self.circuit.ybus, pd.DataFrame) else self.circuit.ybus[k, j]
                
                # ACCUMULATE power with += instead of reassigning
                P_k += V_k * V_j * abs(Y_kj) * np.cos(delta_k - delta_j - np.angle(Y_kj))

            Px[bus_k] = P_k

        return Px

    def calc_Qx(self):
        # Reactive power calculation
        Qx = {bus: 0 for bus in self.bus.index}  # Use self.bus.index for consistency

        for k, bus_k in enumerate(self.bus.index):
            V_k = self.voltage[bus_k]
            delta_k = self.delta[bus_k]
            Q_k = 0  # Initialize reactive power for this bus
            
            for j, bus_j in enumerate(self.bus.index):
                V_j = self.voltage[bus_j]
                delta_j = self.delta[bus_j]
                Y_kj = self.circuit.ybus.iloc[k, j] if isinstance(self.circuit.ybus, pd.DataFrame) else self.circuit.ybus[k, j]
                
                # ACCUMULATE power with += instead of reassigning
                Q_k += V_k * V_j * abs(Y_kj) * np.sin(delta_k - delta_j - np.angle(Y_kj))

            Qx[bus_k] = Q_k

        return Qx

    def initialize_x(self):
        # Create state vector from angles and voltages
        delta_vector = np.array(list(self.delta.values()))
        voltage_vector = np.array(list(self.voltage.values()))
        x = np.concatenate((delta_vector, voltage_vector))
        return x

    def initialize_y(self):
        # This method needs significant revision
        # Start with empty arrays
        real_power_vector = []
        reactive_power_vector = []
        
        # Assuming self.circuit.load is a dictionary of load objects
        if hasattr(self.circuit, 'load') and self.circuit.load:
            # Process all loads
            for load_name, load in self.circuit.load.items():
                # Add load values to vectors (adjusting by base power)
                real_power = load.real_power / s.base_power
                reactive_power = load.reactive_power / s.base_power
                
                # Store these for later use
                load_bus = load.bus.name if hasattr(load.bus, 'name') else load.bus
                real_power_vector.append(real_power)
                reactive_power_vector.append(reactive_power)
        else:
            # Use the single load passed to constructor
            real_power = self.load.real_power / s.base_power
            reactive_power = self.load.reactive_power / s.base_power
            real_power_vector.append(real_power)
            reactive_power_vector.append(reactive_power)
        
        # Convert to numpy arrays
        real_power_array = np.array(real_power_vector)
        reactive_power_array = np.array(reactive_power_vector)
        
        # Combine arrays
        y = np.concatenate((real_power_array, reactive_power_array))
        return y

    def calc_mismatch(self):
        # Calculate mismatch between calculated and specified values
        if self.x is None:
            self.x = self.initialize_x()
        if self.y is None:
            self.y = self.initialize_y()
            
        return self.y - self.x
