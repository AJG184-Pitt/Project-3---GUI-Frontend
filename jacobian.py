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

        