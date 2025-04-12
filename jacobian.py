import numpy as np
import pandas as pd
from circuit import Circuit
from bus import Bus

class BusType:
    SLACK = 1
    PV = 2
    PQ = 3

class Jacobian:
    def __init__(self):
        pass

    def calc_jacobian(self, buses, ybus, angles, voltages):
        """
        Calculate the full Jacobian matrix for Newton-Raphson power flow
        
        Parameters:
            buses: List of Bus objects
            ybus: Complex admittance matrix (can be numpy array or pandas DataFrame)
            angles: Current voltage angles (radians)
            voltages: Current voltage magnitudes (per unit)
            
        Returns:
            J: The complete Jacobian matrix with proper 2x2 block structure
        """
        # Convert pandas DataFrame to numpy array if needed
        if hasattr(ybus, 'values'):
            ybus = ybus.values
        
        # Map string bus types to numeric types
        bus_type_map = {
            "Slack Bus": BusType.SLACK,
            "PV Bus": BusType.PV,
            "PQ Bus": BusType.PQ
        }
        
        n = len(buses)
        
        # Create mapping between bus indices and their variables
        p_index = []     # Buses that contribute to P equations (all except slack)
        q_index = []     # Buses that contribute to Q equations (only PQ buses)
        theta_index = [] # Buses whose theta is a variable (all except slack)
        v_index = []     # Buses whose V is a variable (only PQ buses)
        
        for i, bus in enumerate(buses):
            # Convert string bus type to numeric type if needed
            bus_type = bus_type_map.get(bus.bus_type, bus.bus_type)
            
            if bus_type != BusType.SLACK:
                p_index.append(i)
                theta_index.append(i)
            if bus_type == BusType.PQ:
                q_index.append(i)
                v_index.append(i)
        
        # Calculate the size of each submatrix
        n_p = len(p_index)      # Number of P equations
        n_q = len(q_index)      # Number of Q equations
        n_theta = len(theta_index)  # Number of theta variables
        n_v = len(v_index)      # Number of V variables
        
        # Calculate the total Jacobian size
        j_size = n_p + n_q
        
        # Verify the dimensions match the expected formula
        n_slack = sum(1 for bus in buses if bus_type_map.get(bus.bus_type, bus.bus_type) == BusType.SLACK)
        n_pq = len(q_index)
        
        expected_size = (n - n_slack) + n_pq
        
        # Verify that our j_size calculation is correct
        assert j_size == expected_size, f"Jacobian size mismatch: {j_size} != {expected_size}"
        
        # Initialize the full Jacobian matrix
        J = np.zeros((j_size, j_size))
        
        # Calculate each submatrix using the correct partial derivatives
        J1 = self._calc_j1(buses, ybus, angles, voltages, p_index, theta_index, bus_type_map)
        J2 = self._calc_j2(buses, ybus, angles, voltages, p_index, v_index, bus_type_map)
        J3 = self._calc_j3(buses, ybus, angles, voltages, q_index, theta_index, bus_type_map)
        J4 = self._calc_j4(buses, ybus, angles, voltages, q_index, v_index, bus_type_map)
        
        # Fill the Jacobian with the submatrices
        # J1 (dP/dδ) - upper left block
        J[:n_p, :n_theta] = J1
        
        # J2 (dP/dV) - upper right block
        J[:n_p, n_theta:] = J2
        
        # J3 (dQ/dδ) - lower left block
        J[n_p:, :n_theta] = J3
        
        # J4 (dQ/dV) - lower right block
        J[n_p:, n_theta:] = J4
        
        return J
    
    def _calc_j1(self, buses, ybus, angles, voltages, p_index, theta_index, bus_type_map):
        """
        Calculate J1 submatrix (dP/dδ)
        
        This forms the upper left part of the Jacobian matrix.
        """
        n_p = len(p_index)
        n_theta = len(theta_index)
        j1 = np.zeros((n_p, n_theta))
        
        for i_idx, i in enumerate(p_index):
            for j_idx, j in enumerate(theta_index):
                if i == j:
                    # Diagonal elements
                    sum_term = 0
                    for k in range(len(buses)):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imag
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik * np.sin(theta_ik) - b_ik * np.cos(theta_ik))
                    
                    j1[i_idx, j_idx] = -voltages[i] * sum_term
                else:
                    # Off-diagonal elements
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j1[i_idx, j_idx] = voltages[i] * voltages[j] * (g_ij * np.sin(theta_ij) - b_ij * np.cos(theta_ij))
        
        return j1
    
    def _calc_j2(self, buses, ybus, angles, voltages, p_index, v_index, bus_type_map):
        """
        Calculate J2 submatrix (dP/dV)
        
        This forms the upper right part of the Jacobian matrix.
        """
        n_p = len(p_index)
        n_v = len(v_index)
        j2 = np.zeros((n_p, n_v))
        
        for i_idx, i in enumerate(p_index):
            for j_idx, j in enumerate(v_index):
                if i == j:
                    # Diagonal elements
                    g_ii = ybus[i, i].real
                    
                    # First term
                    first_term = 2 * voltages[i] * g_ii
                    
                    # Calculate sum term
                    sum_term = 0
                    for k in range(len(buses)):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imag
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik * np.cos(theta_ik) + b_ik * np.sin(theta_ik))
                    
                    j2[i_idx, j_idx] = first_term + sum_term
                else:
                    # Off-diagonal elements
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j2[i_idx, j_idx] = voltages[i] * (g_ij * np.cos(theta_ij) + b_ij * np.sin(theta_ij))
        
        return j2
    
    def _calc_j3(self, buses, ybus, angles, voltages, q_index, theta_index, bus_type_map):
        """
        Calculate J3 submatrix (dQ/dδ)
        
        This forms the lower left part of the Jacobian matrix.
        """
        n_q = len(q_index)
        n_theta = len(theta_index)
        j3 = np.zeros((n_q, n_theta))
        
        for i_idx, i in enumerate(q_index):
            for j_idx, j in enumerate(theta_index):
                if i == j:
                    # Diagonal elements
                    sum_term = 0
                    for k in range(len(buses)):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imag
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik * np.cos(theta_ik) + b_ik * np.sin(theta_ik))
                    
                    j3[i_idx, j_idx] = voltages[i] * sum_term
                else:
                    # Off-diagonal elements
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j3[i_idx, j_idx] = -voltages[i] * voltages[j] * (g_ij * np.cos(theta_ij) + b_ij * np.sin(theta_ij))
        
        return j3
    
    def _calc_j4(self, buses, ybus, angles, voltages, q_index, v_index, bus_type_map):
        """
        Calculate J4 submatrix (dQ/dV)
        
        This forms the lower right part of the Jacobian matrix.
        """
        n_q = len(q_index)
        n_v = len(v_index)
        j4 = np.zeros((n_q, n_v))
        
        for i_idx, i in enumerate(q_index):
            for j_idx, j in enumerate(v_index):
                if i == j:
                    # Diagonal elements
                    b_ii = ybus[i, i].imag
                    
                    # First term
                    first_term = -2 * voltages[i] * b_ii
                    
                    # Calculate sum term
                    sum_term = 0
                    for k in range(len(buses)):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imag
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik * np.sin(theta_ik) - b_ik * np.cos(theta_ik))
                    
                    j4[i_idx, j_idx] = first_term + sum_term
                else:
                    # Off-diagonal elements
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j4[i_idx, j_idx] = voltages[i] * (g_ij * np.sin(theta_ij) - b_ij * np.cos(theta_ij))
        
        return j4

# Example usage with your Circuit class:
if __name__ == '__main__':
    # Create a test circuit
    circuit = Circuit("Test Circuit")
        
    # Add buses with different types
    bus1 = Bus("Bus1", 132)
    bus1.bus_type = 'Slack Bus'
    bus2 = Bus("Bus2", 132)
    bus2.bus_type = 'PV Bus'
    bus3 = Bus("Bus3", 33)
    bus3.bus_type = 'PQ Bus'
    
    circuit.buses = {"Bus1": bus1, "Bus2": bus2, "Bus3": bus3}
    
    # Create a sample Ybus matrix
    circuit.ybus = pd.DataFrame([
        [complex(1.5, -4.0), complex(-0.5, 1.0), complex(-1.0, 3.0)],
        [complex(-0.5, 1.0), complex(1.0, -3.0), complex(-0.5, 2.0)],
        [complex(-1.0, 3.0), complex(-0.5, 2.0), complex(1.5, -5.0)]
    ])
    
    # Extract bus data
    angles = np.array([bus.delta for bus in circuit.buses.values()])
    voltages = np.array([bus.vpu for bus in circuit.buses.values()])

    # Create Jacobian instance
    jacobian = Jacobian()
    
    # Calculate the Jacobian
    J = jacobian.calc_jacobian(list(circuit.buses.values()), circuit.ybus, angles, voltages)
    # Alternatively, you could use the extension method:
    # J = calc_jacobian_for_circuit(circuit)
    
    print("Jacobian Matrix:")
    print(np.round(J, 4))
