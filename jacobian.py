import numpy as np
from enum import Enum

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
            ybus: Complex admittance matrix
            angles: Current voltage angles (radians)
            voltages: Current voltage magnitudes (per unit)
            
        Returns:
            J: The complete Jacobian matrix with proper 2x2 block structure
            
        Implementation notes:
        - This follows the structure defined in the milestone document
        - Properly excludes slack bus from calculations
        - Only includes P equations for PV buses, not Q equations
        - Jacobian has the structure:
          J = | J1  J2 |
              | J3  J4 |
        """
        n = len(buses)
        
        # Create mapping between bus indices and their variables
        # This helps us keep track of which buses contribute to which parts of the Jacobian
        p_index = []     # Buses that contribute to P equations (all except slack)
        q_index = []     # Buses that contribute to Q equations (only PQ buses)
        theta_index = [] # Buses whose theta is a variable (all except slack)
        v_index = []     # Buses whose V is a variable (only PQ buses)
        
        for i, bus in enumerate(buses):
            if bus.bus_type != BusType.SLACK:
                p_index.append(i)
                theta_index.append(i)
            if bus.bus_type == BusType.PQ:
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
        # The correct size is (n-n_slack) + n_pq, which is the sum of:
        # - P equations: n - n_slack (all buses except slack)
        # - Q equations: n_pq (only PQ buses)
        n_slack = sum(1 for bus in buses if bus.bus_type == BusType.SLACK)
        n_pv = sum(1 for bus in buses if bus.bus_type == BusType.PV)
        n_pq = len(q_index)
        
        expected_size = (n - n_slack) + n_pq
        
        # Verify that our j_size calculation is correct
        assert j_size == expected_size, f"Jacobian size mismatch: {j_size} != {expected_size}"
        
        # Initialize the full Jacobian matrix
        J = np.zeros((j_size, j_size))
        
        # Calculate each submatrix using the correct partial derivatives
        J1 = self._calc_j1(buses, ybus, angles, voltages, p_index, theta_index)
        J2 = self._calc_j2(buses, ybus, angles, voltages, p_index, v_index)
        J3 = self._calc_j3(buses, ybus, angles, voltages, q_index, theta_index)
        J4 = self._calc_j4(buses, ybus, angles, voltages, q_index, v_index)
        
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
    
    def _calc_j1(self, buses, ybus, angles, voltages, p_index, theta_index):
        """
        Calculate J1 submatrix (dP/dδ)
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
    
    def _calc_j2(self, buses, ybus, angles, voltages, p_index, v_index):
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
    
    def _calc_j3(self, buses, ybus, angles, voltages, q_index, theta_index):
        """
        Calculate J3 submatrix (dQ/dδ)
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
    
    def _calc_j4(self, buses, ybus, angles, voltages, q_index, v_index):
        """
        Calculate J4 submatrix (dQ/dV)
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


if __name__ == '__main__':
    buses = [
        Bus("Bus 1", 1, BusType.SLACK),
        Bus("Bus 2", 2, BusType.PV),
        Bus("Bus 3", 3, BusType.PQ),
    ]
    
    # Create a sample Ybus matrix for a 3-bus system
    # This should match the Ybus from Powerworld for your validation
    ybus = np.array([
        [complex(1.5, -4.0), complex(-0.5, 1.0), complex(-1.0, 3.0)],
        [complex(-0.5, 1.0), complex(1.0, -3.0), complex(-0.5, 2.0)],
        [complex(-1.0, 3.0), complex(-0.5, 2.0), complex(1.5, -5.0)]
    ])
    
    # Set initial voltage angles (radians) and magnitudes (per unit)
    # These will typically come from a flat start or previous iteration
    angles = np.array([0.0, 0.0, 0.0])  # Flat start
    voltages = np.array([1.0, 1.0, 1.0])  # Flat start
    
    # Calculate the Jacobian
    jacobian = Jacobian()
    J = jacobian.calc_jacobian(buses, ybus, angles, voltages)
    
    print("Jacobian Matrix:")
    print(np.round(J, 4))  # Round to 4 decimal places for readability
    
    # Expected size calculation
    n = len(buses)  # Total number of buses
    n_slack = sum(1 for bus in buses if bus.bus_type == BusType.SLACK)  # Number of slack buses
    n_pv = sum(1 for bus in buses if bus.bus_type == BusType.PV)  # Number of PV buses
    n_pq = sum(1 for bus in buses if bus.bus_type == BusType.PQ)  # Number of PQ buses
    
    # The correct size calculation:
    # P equations: (n - n_slack) = number of non-slack buses
    # Q equations: n_pq = number of PQ buses
    # Total equations = (n - n_slack) + n_pq
    # Which simplifies to: n - n_slack + n_pq
    expected_size = (n - n_slack) + n_pq
    
    print(f"Bus Configuration: {n_slack} Slack, {n_pv} PV, {n_pq} PQ buses")
    print(f"Total Jacobian size: {expected_size}x{expected_size}")
    print(f"Actual size: {J.shape}")
    
    # Alternative calculation using the formula from milestone document
    # (2N-2-number of PV buses)
    alt_expected_size = 2*n - 2 - n_pv
    print(f"Size from milestone formula: {alt_expected_size}x{alt_expected_size}")
