import numpy as np
from numpy.linalg import solve
from enum import Enum

# Import the Jacobian class from milestone 7
from jacobian import Jacobian, BusType

class PowerFlow:
    """
    Newton-Raphson power flow solver class for electrical power systems.
    This class iteratively solves for bus voltage magnitudes and angles
    using the Jacobian matrix and power mismatches.
    """
    
    def __init__(self):
        """Initialize the PowerFlow solver."""
        pass
    
    def solve(self, buses, ybus, tol=0.001, max_iter=50):
        """
        Solve the power flow problem using the Newton-Raphson method.
        
        Parameters:
        -----------
        buses : list or array
            List of bus objects containing bus parameters and types
        ybus : numpy.ndarray
            Admittance matrix of the power system
        tol : float, optional
            Convergence tolerance, default is 0.001
        max_iter : int, optional
            Maximum number of iterations, default is 50
            
        Returns:
        --------
        dict
            Dictionary containing the solved voltages, angles, iterations, and convergence status
        """
        # Step 2: Initialize Variables
        n_bus = len(buses)
        
        # Extract initial voltage magnitudes and angles (flat start if not provided)
        v_mag = np.ones(n_bus)
        v_ang = np.zeros(n_bus)
        
        # Extract voltage and angle values from buses
        for i, bus in enumerate(buses):
            v_mag[i] = bus.vpu  # Use vpu from Bus class
            v_ang[i] = bus.delta  # Use delta from Bus class
        
        # Initialize iteration counter and convergence flag
        iter_count = 0
        converged = False
        
        # Map string bus types to enum values
        bus_type_map = {
            "Slack Bus": BusType.SLACK,
            "PV Bus": BusType.PV,
            "PQ Bus": BusType.PQ
        }
        
        # Get bus types
        bus_types = [bus_type_map.get(bus.bus_type, BusType.PQ) for bus in buses]
        
        # Identify PV, PQ, and slack buses
        pv_buses = [i for i, bus_type in enumerate(bus_types) if bus_type == BusType.PV]
        pq_buses = [i for i, bus_type in enumerate(bus_types) if bus_type == BusType.PQ]
        slack_buses = [i for i, bus_type in enumerate(bus_types) if bus_type == BusType.SLACK]
        
        # Set up indices for the Jacobian matrix (excluding slack bus)
        non_slack_buses = [i for i in range(n_bus) if i not in slack_buses]
        
        # Get scheduled P and Q values - temporary placeholder
        # In a real system, you'd compute this from generation and load data
        p_scheduled = np.zeros(n_bus)
        q_scheduled = np.zeros(n_bus)
        
        # For testing, set some values for PV and PQ buses
        for i in pv_buses:
            p_scheduled[i] = 0.5  # Example P value for PV buses
        
        for i in pq_buses:
            p_scheduled[i] = -0.5  # Example P value for PQ buses (negative for load)
            q_scheduled[i] = -0.3  # Example Q value for PQ buses (negative for load)
        
        # Store convergence history
        mismatch_history = []
        
        # Step 3: Iterative Solution Loop
        while not converged and iter_count < max_iter:
            # Step 1: Calculate power mismatches
            p_calc, q_calc = self._calculate_power(v_mag, v_ang, ybus)
            
            # Compute power mismatches (excluding slack bus)
            p_mismatch = p_scheduled[non_slack_buses] - p_calc[non_slack_buses]
            q_mismatch = q_scheduled[pq_buses] - q_calc[pq_buses]
            
            # Combine P and Q mismatches for convergence check
            mismatch = np.concatenate((p_mismatch, q_mismatch))
            max_mismatch = np.max(np.abs(mismatch))
            mismatch_history.append(max_mismatch)
            
            # Step 5: Check convergence
            if max_mismatch < tol:
                converged = True
                break
                
            # Step 2: Build Jacobian matrix
            J = self._build_jacobian(v_mag, v_ang, ybus, non_slack_buses, pq_buses)
            
            # Step 3: Solve the linear system J * Δx = mismatch
            delta_x = solve(J, mismatch)
            
            # Extract voltage angle and magnitude corrections
            n_delta = len(non_slack_buses)
            delta_theta = delta_x[:n_delta]
            delta_v = delta_x[n_delta:]
            
            # Step 4: Update voltages and angles based on bus types
            # Update voltage angles (excluding slack bus)
            for i, idx in enumerate(non_slack_buses):
                v_ang[idx] += delta_theta[i]
            
            # Update voltage magnitudes (PQ buses only)
            for i, idx in enumerate(pq_buses):
                v_mag[idx] += delta_v[i]
            
            iter_count += 1
        
        # Update bus objects with the final values
        for i, bus in enumerate(buses):
            bus.vpu = v_mag[i]
            bus.delta = v_ang[i]
        
        # Prepare results
        results = {
            'v_mag': v_mag,
            'v_ang': v_ang,
            'iterations': iter_count,
            'converged': converged,
            'mismatch_history': mismatch_history,
            'final_mismatch': max_mismatch if iter_count > 0 else 0.0
        }
        
        # Add calculated P and Q values to results
        if converged:
            p_calc, q_calc = self._calculate_power(v_mag, v_ang, ybus)
            results['p_calc'] = p_calc
            results['q_calc'] = q_calc
        
        # Step 6: Report non-convergence if max iterations exceeded
        if not converged:
            print(f"WARNING: Power flow did not converge after {max_iter} iterations.")
            print(f"Maximum mismatch: {max_mismatch}")
        
        return results
    
    def _calculate_power(self, v_mag, v_ang, ybus):
        """
        Calculate active and reactive power injections at each bus.
        This is a placeholder for Milestone 6's power mismatch function.
        
        Parameters:
        -----------
        v_mag : numpy.ndarray
            Voltage magnitudes
        v_ang : numpy.ndarray
            Voltage angles
        ybus : numpy.ndarray
            Admittance matrix
            
        Returns:
        --------
        tuple
            (P, Q) - Active and reactive power injections
        """
        n_bus = len(v_mag)
        
        # Convert polar to complex voltages
        v = v_mag * np.exp(1j * v_ang)
        
        # Sparse to dense conversion for calculations if needed
        ybus_dense = ybus.toarray() if hasattr(ybus, 'toarray') else ybus
        
        # Initialize power vectors
        p = np.zeros(n_bus)
        q = np.zeros(n_bus)
        
        # Calculate P and Q at each bus
        for i in range(n_bus):
            for j in range(n_bus):
                # Get admittance components
                y_ij = ybus_dense[i, j]
                g_ij = np.real(y_ij)
                b_ij = np.imag(y_ij)
                
                # Get angle difference
                theta_ij = v_ang[i] - v_ang[j]
                
                # Calculate P and Q components
                p[i] += v_mag[i] * v_mag[j] * (g_ij * np.cos(theta_ij) + b_ij * np.sin(theta_ij))
                q[i] += v_mag[i] * v_mag[j] * (g_ij * np.sin(theta_ij) - b_ij * np.cos(theta_ij))
        
        return p, q
    
    def _build_jacobian(self, v_mag, v_ang, ybus, non_slack_buses, pq_buses):
        """
        Build the Jacobian matrix for the Newton-Raphson power flow using the Jacobian class from Milestone 7.
        
        Parameters:
        -----------
        v_mag : numpy.ndarray
            Voltage magnitudes
        v_ang : numpy.ndarray
            Voltage angles
        ybus : numpy.ndarray
            Admittance matrix
        non_slack_buses : list
            Indices of non-slack buses
        pq_buses : list
            Indices of PQ buses
            
        Returns:
        --------
        numpy.ndarray
            Jacobian matrix
        """
        # Create a list of buses with appropriate bus types for the Jacobian calculator
        class TempBus:
            def __init__(self, bus_type):
                self.bus_type = bus_type
                
        buses = []
        n_bus = len(v_mag)
        
        # Determine bus types from the provided lists
        for i in range(n_bus):
            if i not in non_slack_buses:
                # This is a slack bus
                buses.append(TempBus(BusType.SLACK))
            elif i in pq_buses:
                # This is a PQ bus
                buses.append(TempBus(BusType.PQ))
            else:
                # This is a PV bus
                buses.append(TempBus(BusType.PV))
        
        # Use the Jacobian class from Milestone 7
        jacobian_calculator = Jacobian()
        J = jacobian_calculator.calc_jacobian(buses, ybus, v_ang, v_mag)
        
        return J

if __name__ == "__main__":
    # Example usage:
    from bus import Bus
    import numpy as np
    
    # Create buses
    bus1 = Bus("Bus1", 132, "Slack Bus")
    bus1.vpu = 1.05
    
    bus2 = Bus("Bus2", 132, "PV Bus")
    bus2.vpu = 1.02
    
    bus3 = Bus("Bus3", 33, "PQ Bus")
    
    buses = [bus1, bus2, bus3]
    
    # Create a simple Ybus
    ybus = np.array([
        [complex(10, -30), complex(-5, 15), complex(-5, 15)],
        [complex(-5, 15), complex(10, -30), complex(-5, 15)],
        [complex(-5, 15), complex(-5, 15), complex(10, -30)]
    ])
    
    # Create and run the solver
    solver = PowerFlow()
    results = solver.solve(buses, ybus)
    
    # Print results
    print("Solved voltages:")
    for i, bus in enumerate(buses):
        print(f"{bus.name}: {bus.vpu:.4f} ∠{np.degrees(bus.delta):.2f}°")
