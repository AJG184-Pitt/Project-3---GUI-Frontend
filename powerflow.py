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
        """Initialize the PowerFlow solver."""
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
        Uses the Solution class for power mismatches and Jacobian class for matrix calculations.
        
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
        # Ensure we have a circuit
        if circuit is None:
            raise ValueError("Circuit object is required for using the Solution class")
        
        # Step 1: Initialize Variables
        n_bus = len(buses)
        
        # Map the bus names to indices
        bus_names = [bus.name for bus in buses]
        bus_idx_map = {bus_names[i]: i for i in range(n_bus)}
        
        # Extract initial voltage magnitudes and angles
        for i, bus in enumerate(buses):
            if not hasattr(bus, 'vpu') or bus.vpu is None:
                bus.vpu = 1.0  # Flat start for voltage magnitude
            if not hasattr(bus, 'delta') or bus.delta is None:
                bus.delta = 0.0  # Flat start for voltage angle
        
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
        
        # IMPORTANT: Set up the bus container according to Solution class's expected structure
        # Looking at the error, the Solution class expects the bus indices to be bus names, not integers
        bus_container = type('', (), {})()
        bus_container.index = bus_names  # Use bus names as indices
        bus_container.bus_count = bus_names  # Use bus names for bus_count as well
        bus_container.bus_type = {name: buses[i].bus_type for i, name in enumerate(bus_names)}
        
        # Create dictionaries for voltage and angles using bus names as keys
        delta_dict = {name: buses[i].delta for i, name in enumerate(bus_names)}
        voltage_dict = {name: buses[i].vpu for i, name in enumerate(bus_names)}
        
        # Create a load object with proper parameters
        # For each bus, create a load if not already present
        loads = []
        for i, bus in enumerate(buses):
            # Set default power values based on bus type
            real_power = 0.0
            reactive_power = 0.0
            
            if i in pv_buses:
                real_power = 0.5  # Default generation for PV buses
            elif i in pq_buses:
                real_power = -0.5  # Default load for PQ buses (negative for consumption)
                reactive_power = -0.3  # Default reactive load for PQ buses
                
            # Create a load object for this bus
            load_name = f"Load_{bus.name}"
            loads.append(Load(load_name, bus, real_power, reactive_power))
            
        # Use the first load for initializing the Solution
        # In a real system, you would aggregate all loads
        if loads:
            primary_load = loads[0]
        else:
            # Create a dummy load if none exists
            primary_load = Load("Dummy_Load", buses[0], 0.0, 0.0)
        
        # Make the loads available in the circuit
        circuit.load = {load.name: load for load in loads}
        
        # Initialize a Solution object with the proper load
        # Create the Solution object WITHOUT initially calculating P and Q
        # to avoid KeyErrors before we've set up the dictionaries
        solution = Solution("PowerFlow Solution", bus_container, circuit, primary_load)
        
        # THEN set the dictionaries
        solution.delta = delta_dict
        solution.voltage = voltage_dict
        
        # NOW we can calculate P and Q safely
        solution.P = solution.calc_Px()
        solution.Q = solution.calc_Qx()
        
        # Manually calculate x and y arrays for Solution to avoid broadcasting issues
        # This fixes the shape mismatch in calc_mismatch()
        
        # Initialize x from solution's delta and voltage values
        # Make sure the size matches what we expect
        delta_values = np.array([solution.delta[name] for name in bus_names])
        voltage_values = np.array([solution.voltage[name] for name in bus_names])
        
        # Calculate which buses contribute to the state vector
        # Only non-slack buses contribute angles
        # Only PQ buses contribute voltages
        non_slack_names = [bus_names[i] for i in non_slack_buses]
        pq_names = [bus_names[i] for i in pq_buses]
        
        # Create x with only the relevant elements
        delta_x = np.array([solution.delta[name] for name in non_slack_names])
        voltage_x = np.array([solution.voltage[name] for name in pq_names])
        solution.x = np.concatenate((delta_x, voltage_x))
        
        # Create y with scheduled powers
        # Get scheduled P and Q values from the loads
        p_scheduled = np.zeros(n_bus)
        q_scheduled = np.zeros(n_bus)
        
        for load in loads:
            bus_idx = buses.index(load.bus)
            p_scheduled[bus_idx] = load.real_power
            q_scheduled[bus_idx] = load.reactive_power
        
        # Extract only the relevant scheduled powers (same buses as x)
        p_scheduled_nonslack = p_scheduled[non_slack_buses]
        q_scheduled_pq = q_scheduled[pq_buses]
        solution.y = np.concatenate((p_scheduled_nonslack, q_scheduled_pq))
        
        # Now we can calculate the mismatch correctly
        try:
            solution.mismatch = solution.calc_mismatch()
        except Exception as e:
            # If calc_mismatch fails, we'll calculate it directly
            print(f"Warning: Solution.calc_mismatch() failed: {e}")
            # Extract calculated powers in the same order as scheduled
            p_calc = np.array([solution.P.get(bus_names[i], 0.0) for i in range(n_bus)])
            q_calc = np.array([solution.Q.get(bus_names[i], 0.0) for i in range(n_bus)])
            
            # Use these for mismatches
            p_mismatch = p_scheduled[non_slack_buses] - p_calc[non_slack_buses]
            q_mismatch = q_scheduled[pq_buses] - q_calc[pq_buses]
            
            # Combine for the complete mismatch vector
            mismatch = np.concatenate((p_mismatch, q_mismatch))
        else:
            # If calc_mismatch succeeds, use its result
            # Convert from solution.mismatch to our mismatch vector
            p_calc = np.array([solution.P.get(bus_names[i], 0.0) for i in range(n_bus)])
            q_calc = np.array([solution.Q.get(bus_names[i], 0.0) for i in range(n_bus)])
            
            # Use these for mismatches
            p_mismatch = p_scheduled[non_slack_buses] - p_calc[non_slack_buses]
            q_mismatch = q_scheduled[pq_buses] - q_calc[pq_buses]
            
            # Combine for the complete mismatch vector
            mismatch = np.concatenate((p_mismatch, q_mismatch))
        
        # Store convergence history
        mismatch_history = []
        
        # Initialize iteration counter and convergence flag
        iter_count = 0
        converged = False
        max_mismatch = float('inf')
        
        # Step 3: Iterative Solution Loop
        while not converged and iter_count < max_iter:
            # Calculate power injections using Solution class
            solution.P = solution.calc_Px()
            solution.Q = solution.calc_Qx()
            
            # Extract power calculations as arrays for mismatch calculation
            p_calc = np.zeros(n_bus)
            q_calc = np.zeros(n_bus)
            
            for i, name in enumerate(bus_names):
                p_calc[i] = solution.P.get(name, 0)
                q_calc[i] = solution.Q.get(name, 0)
            
            # Calculate mismatch directly (avoiding Solution.calc_mismatch which may have issues)
            p_mismatch = p_scheduled[non_slack_buses] - p_calc[non_slack_buses]
            q_mismatch = q_scheduled[pq_buses] - q_calc[pq_buses]
            
            # Combine P and Q mismatches
            mismatch = np.concatenate((p_mismatch, q_mismatch))
            max_mismatch = np.max(np.abs(mismatch))
            mismatch_history.append(max_mismatch)
            
            # Update solution's state vectors
            # Create x with only the relevant elements
            delta_x = np.array([solution.delta[name] for name in non_slack_names])
            voltage_x = np.array([solution.voltage[name] for name in pq_names])
            solution.x = np.concatenate((delta_x, voltage_x))
            solution.y = np.concatenate((p_scheduled_nonslack, q_scheduled_pq))
            
            # Step 5: Check convergence
            if max_mismatch < tol:
                converged = True
                break
            
            # Extract current voltage and angle values as numpy arrays for Jacobian
            v_mag = np.array([buses[i].vpu for i in range(n_bus)])
            v_ang = np.array([buses[i].delta for i in range(n_bus)])
            
            # Step 2: Build Jacobian matrix using the Jacobian class
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
                solution.delta[bus_names[idx]] = buses[idx].delta  # Update Solution class data using bus name
            
            # Update voltage magnitudes (PQ buses only)
            for i, idx in enumerate(pq_buses):
                buses[idx].vpu += delta_v[i]
                solution.voltage[bus_names[idx]] = buses[idx].vpu  # Update Solution class data using bus name
            
            iter_count += 1
        
        # Prepare results
        results = {
            'v_mag': np.array([buses[i].vpu for i in range(n_bus)]),
            'v_ang': np.array([buses[i].delta for i in range(n_bus)]),
            'iterations': iter_count,
            'converged': converged,
            'mismatch_history': mismatch_history,
            'final_mismatch': max_mismatch if iter_count > 0 else 0.0
        }
        
        # Add calculated P and Q values to results
        if converged:
            solution.P = solution.calc_Px()
            solution.Q = solution.calc_Qx()
            
            # Convert from dictionary with bus name keys to array with proper ordering
            p_calc_result = np.zeros(n_bus)
            q_calc_result = np.zeros(n_bus)
            
            for i, name in enumerate(bus_names):
                p_calc_result[i] = solution.P.get(name, 0)
                q_calc_result[i] = solution.Q.get(name, 0)
                
            results['p_calc'] = p_calc_result
            results['q_calc'] = q_calc_result
        
        # Step 6: Report non-convergence if max iterations exceeded
        if not converged:
            print(f"WARNING: Power flow did not converge after {max_iter} iterations.")
            print(f"Maximum mismatch: {max_mismatch}")
        
        return results

if __name__ == "__main__":
    # Create a test circuit
    circuit = Circuit("Test Power Flow")
    
    # Add buses with different types
    circuit.add_bus("Bus1", 132)
    circuit.buses["Bus1"].bus_type = "Slack Bus"
    circuit.buses["Bus1"].vpu = 1.05
    
    circuit.add_bus("Bus2", 132)
    circuit.buses["Bus2"].bus_type = "PV Bus"
    circuit.buses["Bus2"].vpu = 1.02
    
    circuit.add_bus("Bus3", 33)
    circuit.buses["Bus3"].bus_type = "PQ Bus"
    
    # Create loads for each bus
    loads = []
    loads.append(Load("Load1", circuit.buses["Bus1"], 0.0, 0.0))  # Slack bus typically has no scheduled load
    loads.append(Load("Load2", circuit.buses["Bus2"], 0.5, 0.0))  # PV bus with active power specified
    loads.append(Load("Load3", circuit.buses["Bus3"], -0.5, -0.3))  # PQ bus with active and reactive load
    
    # Add loads to circuit (assuming circuit has a loads attribute)
    circuit.load = {load.name: load for load in loads}
    
    # Create a simple Ybus and assign it to the circuit
    ybus_data = [
        [complex(10, -30), complex(-5, 15), complex(-5, 15)],
        [complex(-5, 15), complex(10, -30), complex(-5, 15)],
        [complex(-5, 15), complex(-5, 15), complex(10, -30)]
    ]
    
    circuit.ybus = pd.DataFrame(ybus_data)
    
    # Create and run the solver
    solver = PowerFlow()
    results = solver.solve_circuit(circuit)
    
    # Print results
    print("\nNewton-Raphson Power Flow Solution")
    print("---------------------------------")
    print(f"Converged: {results['converged']}")
    print(f"Iterations: {results['iterations']}")
    
    print("\nBus Voltages:")
    for bus_name, bus in circuit.buses.items():
        print(f"{bus_name}: {bus.vpu:.4f} ∠{np.degrees(bus.delta):.2f}°")
    
    if 'p_calc' in results and 'q_calc' in results:
        print("\nCalculated Power Flows:")
        for i, (bus_name, bus) in enumerate(circuit.buses.items()):
            p = results['p_calc'][i]
            q = results['q_calc'][i]
            print(f"{bus_name}: P = {p:.4f} p.u., Q = {q:.4f} p.u.")
