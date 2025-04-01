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
        Calculate the full Jacobian matrix for Newton-Raphson power flow
        """
        
        n = len(buses)

        # Count different bus types
        n_pv = sum(1 for bus in buses if bus.type == BusType.PV)
        n_pq = sum(1 for bus in buses if bus.type == BusType.PQ)

        # Determine Jacobian dimensions
        j_size = 2*n - 2 - n_pv

        # Initialize J1-4 submatrices
        j1 = np.zeros((n, n))
        j2 = np.zeros((n, n))
        j3 = np.zeros((n, n))
        j4 = np.zeros((n, n))

        # Calculate each submatric
        j1 = self._calc_j1(buses, ybus, angles, voltages)
        j2 = self._calc_j2(buses, ybus, angles, voltages)
        j3 = self._calc_j3(buses, ybus, angles, voltages)
        j4 = self._calc_j4(buses, ybus, angles, voltages)

        # Create mapping between bus indicies and P,Q row
        p_index = []
        q_index = []

        for i, bus in enumerate(buses):
            if bus.type != BusType.SLACK:
                p_index.append(i)
            if bus.type == BusType.PQ:
                q_index.append(i)

        # Create mapping between bus indicies and corresponding theta,V columns
        theta_index = []
        v_index = []

        for i, bus in enumerate(buses):
            if bus.type != BusType.SLACK:
                theta_index.append(i)
            if bus.type == BusType.PQ:
                v_index.append(i)
        
        # Initialize final index
        J = np.zeros((j_size, j_size))

        # Fill J1 quadrant
        np_rows = len(p_index)
        ntheta_cols = len(theta_index)
        for i, p_i in enumerate(p_index):
            for j, theta_j in enumerate(theta_index):
                J[i, j] = j1[p_i, theta_j]

        # Fill J2 quadrant
        nv_cols = len(v_index)
        for i, p_i in enumerate(p_index):
            for j, v_j in enumerate(v_index):
                J[i, ntheta_cols + j] = j2[p_i, v_j]

        # Fill J3 quadrant
        nq_rows = len(q_index)
        for i, q_i in enumerate(q_index):
            for j, theta_j in enumerate(theta_index):
                J[np_rows + i, j] = j3[q_i, theta_j]

        # Fill J4 quadrant
        for i, q_i in enumerate(q_index):
            for j, v_j in enumerate(v_index):
                J[np_rows + i, ntheta_cols + j] = j4[q_i, v_j]

        return J
    
    def _calc_j1(self, buses, ybus, angles, voltages):
        """
        Calculate J1 submatrix (d_P/d_theta)
        """

        n = len(buses)
        j1 = np.zeroes((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    # Calculate sum term for diag elements
                    sum_term = 0
                    for k in range(n):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imag
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik *
                                                       np.sin(theta_ik) - b_ik * np.cos(theta_ik))
                            
                    j1[i, i] = voltages[i] * sum_term
                else:
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j1[i, j] = voltages[i] * voltages[j] * (g_ij * 
                                                            np.sin(theta_ij) - b_ij * np.cos(theta_ij))
                    
        return j1
    
    def _calc_j2(self, buses, ybus, angles, voltages):
        """
        Calculate J2 submatrix (dP/dV)
        """
        
        n = len(buses)
        j2 = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    g_ii = ybus[i, i].real
                    first_term = 2 * g_ii * voltages[i]

                    # Calculate sum term
                    sum_term = 0
                    for k in range(n):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imagg
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik *
                                                       np.cos(theta_ik) + b_ik * np.sin(theta_ik))
                            
                    j2[i, j] = first_term + sum_term
                else:
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j2[i, j] = voltages[i] * (g_ij * np.cos(theta_ij) +
                                              b_ij * np.sin(theta_ij))
                    
        return j2
    
    def _calc_j3(self, buses, ybus, angles, voltages):
        """
        Calculate J3 submatrix (dQ/d-theta)
        """


        n = len(buses)
        j3 = np.zero((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    sum_term = 0
                    for k in range(n):
                        if k != i:
                            g_ik = ybus[i, j].real
                            b_ik = ybus[i, j].imag
                            theta_ik = angles[i] - angles[j]
                            sum_term += voltages[k] * (g_ik *
                                                       np.cos(theta_ik) + b_ik * np.sin(theta_ik))
                            
                    j3[i, j] = voltages[i] * sum_term
                else:
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j3[i, j] = -voltages[i] * voltages[j] * (g_ij * 
                                                            np.cos(theta_ij) + b_ij * np.sin(theta_ij))
        return j3
    
    def _calc_j4(self, buses, ybus, angles, voltages):
        """
        Calculate J4 submatrix (dQ/dV)
        """

        n = len(buses)
        j4 = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i == j:
                    b_ii = ybus[i, i].imag
                    first_term = -2 * b_ii * voltages[i]

                    # Calculate sum term
                    sum_term = 0
                    for k in range(0):
                        if k != i:
                            g_ik = ybus[i, k].real
                            b_ik = ybus[i, k].imag
                            theta_ik = angles[i] - angles[k]
                            sum_term += voltages[k] * (g_ik * np.sin(theta_ik) - 
                                                       b_ik * np.cos(theta_ik))
                            
                    j4[i, j] = first_term + sum_term
                else:
                    g_ij = ybus[i, j].real
                    b_ij = ybus[i, j].imag
                    theta_ij = angles[i] - angles[j]
                    j4[i, j] = voltages[i] * (g_ij * np.sin(theta_ij) - 
                                              b_ij * np.cos(theta_ij))
        return j4
