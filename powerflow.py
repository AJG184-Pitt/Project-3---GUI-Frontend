import numpy as np
from numpy.linalg import solve
from enum import Enum
import pandas as pd
from circuit import Circuit
from bus import Bus

# Import the Jacobian class
from jacobian import Jacobian, BusType

# Import the Solution class for power mismatches
from solution import Solution
from load import Load

class PowerFlow:
    """
    Newton-Raphson power flow solver class for electrical power systems.
    This class iteratively solves for bus voltage magnitudes and angles
    using the Solution class for power mismatches and the Jacobian class.
    """
    
    def __init__(self, circuit):
        """Initialize the PowerFlow solver with a circuit."""
        self.jacobian = Jacobian(circuit)
    
    def solve_circuit(self, circuit, tol=0.001, max_iter=50):
        """
        Solve the power flow problem for a Circuit object using the Newton-Raphson method.
        
        Parameters:
        -----------
        circuit : Circuit
            Circuit object containing buses and components
        tol : float, optional
            Convergence tolerance, default is 0.001
        max_iter : int, optional
            Maximum number of iterations, default is 50
            
        Returns:
        --------
        dict
            Dictionary containing the solved voltages, angles, iterations, and convergence status
        """
        # Make sure Ybus is calculated
        if circuit.ybus is None:
            circuit.calc_ybus()
            
        # Extract buses from circuit
        buses = list(circuit.buses.values())
        
        # Call the main solve method
        return self.solve(buses, circuit.ybus, tol, max_iter, circuit)
    
    def solve(self, buses, ybus, tol=0.001, max_iter=50, circuit=None):
        """
        Solve the power flow problem using the Newton-Raphson method.
        
        Parameters:
        -----------
        buses : list of Bus objects
            List of bus objects containing bus parameters and types
        ybus : numpy.ndarray or pandas.DataFrame
            Admittance matrix of the power system
        tol : float, optional
            Convergence tolerance, default is 0.001
        max_iter : int, optional
            Maximum number of iterations, default is 50
        circuit : Circuit, optional
            Circuit object containing the power system
            
        Returns:
        --------
        dict
            Dictionary containing the solved voltages, angles, iterations, and convergence status
        """
        # 1. Initialize Variables
        n_bus = len(buses)
        
        # Map the bus names to indices
        bus_names = [bus.name for bus in buses]
        
        # Ensure each bus has initial values (flat start if not specified)
        for bus in buses:
            if not hasattr(bus, 'vpu') or bus.vpu is None:
                bus.vpu = 1.0  # Flat start for voltage magnitude
            if not hasattr(bus, 'delta') or bus.delta is None:
                bus.delta = 0.0  # Flat start for voltage angle (in radians)
        
        # Map string bus types to enum values
        bus_type_map = {
            "Slack Bus": BusType.SLACK,
            "PV Bus": BusType.PV,
            "PQ Bus": BusType.PQ
        }
        
        # Get bus types and identify different bus categories
        bus_types = [bus_type_map.get(bus.bus_type, BusType.PQ) for bus in buses]
        
        # Identify PV, PQ, and slack buses by their indices
        pv_buses = [i for i, bus_type in enumerate(bus_types) if bus_type == BusType.PV]
        pq_buses = [i for i, bus_type in enumerate(bus_types) if bus_type == BusType.PQ]
        slack_buses = [i for i, bus_type in enumerate(bus_types) if bus_type == BusType.SLACK]
        
        # Set up indices for variables in the Jacobian (excluding slack bus)
        non_slack_buses = [i for i in range(n_bus) if i not in slack_buses]
        
        # Set up for Solution class
        solution = self._setup_solution(buses, circuit, bus_names)
        
        # Initialize iteration counter and convergence flag
        iter_count = 0
        converged = False
        max_mismatch = float('inf')
        mismatch_history = []  # To track convergence progress
        
        # Extract initial voltage and angle values as arrays
        v_mag = np.array([bus.vpu for bus in buses])
        v_ang = np.array([bus.delta for bus in buses])
        
        # Extract scheduled power values for buses
        p_scheduled, q_scheduled = self._get_scheduled_powers(buses, circuit)
        
        # 3. Iterative Solution Loop
        while not converged and iter_count < max_iter:
            # Step 1: Calculate power injections and mismatches
            p_calc, q_calc = self._calculate_power_injections(buses, ybus, v_mag, v_ang)
            
            # Calculate mismatches (excluding slack bus for P, and slack+PV buses for Q)
            p_mismatch = p_scheduled[non_slack_buses] - p_calc[non_slack_buses]
            q_mismatch = q_scheduled[pq_buses] - q_calc[pq_buses]
            
            # Combine for complete mismatch vector
            mismatch = np.concatenate((p_mismatch, q_mismatch))
            max_mismatch = np.max(np.abs(mismatch))
            mismatch_history.append(max_mismatch)
            
            # Step 5: Check convergence
            if max_mismatch < tol:
                converged = True
                break
            
            # Step 2: Build Jacobian matrix
            J = self.jacobian.calc_jacobian(buses, ybus, v_ang, v_mag)
            
            # Step 3: Solve the linear system J * Δx = mismatch
            delta_x = solve(J, mismatch)
            
            # Extract voltage angle and magnitude corrections
            n_delta = len(non_slack_buses)
            delta_theta = delta_x[:n_delta]
            delta_v = delta_x[n_delta:]
            
            # Step 4: Update voltages and angles based on bus types
            # Update voltage angles (excluding slack bus)
            for i, idx in enumerate(non_slack_buses):
                buses[idx].delta += delta_theta[i]
                v_ang[idx] = buses[idx].delta
            
            # Update voltage magnitudes (PQ buses only)
            for i, idx in enumerate(pq_buses):
                buses[idx].vpu += delta_v[i]
                v_mag[idx] = buses[idx].vpu
            
            iter_count += 1
        
        # Step 6: Report non-convergence if max iterations exceeded
        if not converged:
            print(f"WARNING: Power flow did not converge after {max_iter} iterations.")
            print(f"Maximum mismatch: {max_mismatch}")
        
        # Calculate final power injections if converged
        if converged:
            p_calc, q_calc = self._calculate_power_injections(buses, ybus, v_mag, v_ang)
        
        # Prepare results dictionary
        results = {
            'v_mag': v_mag,
            'v_ang': v_ang,
            'iterations': iter_count,
            'converged': converged,
            'mismatch_history': mismatch_history,
            'final_mismatch': max_mismatch if iter_count > 0 else 0.0
        }
        
        if converged:
            results['p_calc'] = p_calc
            results['q_calc'] = q_calc
        
        return results
    
    def _setup_solution(self, buses, circuit, bus_names):
        """Helper method to set up the Solution object."""
        # Create a bus container for the Solution class
        bus_container = type('', (), {})()
        bus_container.index = bus_names
        bus_container.bus_count = bus_names
        bus_container.bus_type = {bus.name: bus.bus_type for bus in buses}
        
        # Create dictionaries for voltage and angles
        delta_dict = {bus.name: bus.delta for bus in buses}
        voltage_dict = {bus.name: bus.vpu for bus in buses}
        
        # Create a load if needed
        if hasattr(circuit, 'load') and circuit.load:
            primary_load = list(circuit.load.values())[0]
        else:
            primary_load = Load("Dummy_Load", buses[0], 0.0, 0.0)
        
        # Initialize solution object
        solution = Solution("PowerFlow Solution", bus_container, circuit, primary_load)
        solution.delta = delta_dict
        solution.voltage = voltage_dict
        solution.P = solution.calc_Px()
        solution.Q = solution.calc_Qx()
        
        return solution
    
    def _get_scheduled_powers(self, buses, circuit):
        """Extract scheduled power values from buses and loads."""
        n_bus = len(buses)
        p_scheduled = np.zeros(n_bus)
        q_scheduled = np.zeros(n_bus)
        
        # Add bus generation (if any)
        for i, bus in enumerate(buses):
            if hasattr(bus, 'p_gen'):
                p_scheduled[i] += bus.p_gen
            if hasattr(bus, 'q_gen'):
                q_scheduled[i] += bus.q_gen
                
        # Add load contributions (load is taken as negative power)
        if hasattr(circuit, 'load') and circuit.load:
            for load in circuit.load.values():
                bus_idx = buses.index(load.bus)
                p_scheduled[bus_idx] -= load.real_power
                q_scheduled[bus_idx] -= load.reactive_power
        
        return p_scheduled, q_scheduled
    
    def _calculate_power_injections(self, buses, ybus, v_mag, v_ang):
        """Calculate active and reactive power injections at all buses."""
        n_bus = len(buses)
        p_calc = np.zeros(n_bus)
        q_calc = np.zeros(n_bus)
        
        # Convert ybus to numpy array if it's a DataFrame
        if hasattr(ybus, 'values'):
            y_matrix = ybus.values
        else:
            y_matrix = ybus
        
        # Calculate power injections using the power flow equations
        for i in range(n_bus):
            for j in range(n_bus):
                y_ij = y_matrix[i, j]
                y_ij_abs = abs(y_ij)
                theta_ij = np.angle(y_ij)
                
                angle_diff = v_ang[i] - v_ang[j]
                
                p_calc[i] += v_mag[i] * v_mag[j] * y_ij_abs * np.cos(angle_diff - theta_ij)
                q_calc[i] += v_mag[i] * v_mag[j] * y_ij_abs * np.sin(angle_diff - theta_ij)
        
        return p_calc, q_calc
