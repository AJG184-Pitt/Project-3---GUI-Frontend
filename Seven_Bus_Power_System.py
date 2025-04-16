from circuit import Circuit
from jacobian import Jacobian
import numpy as np
from powerflow import PowerFlow
from solution import Solution
from load import Load

circuit1 = Circuit("Test Circuit")

#adding the 7 buses
circuit1.add_bus("Bus1", 20)
circuit1.add_bus("Bus2", 230)
circuit1.add_bus("Bus3", 230)
circuit1.add_bus("Bus4", 230)
circuit1.add_bus("Bus5", 230)
circuit1.add_bus("Bus6", 230)
circuit1.add_bus("Bus7", 18)

circuit1.buses["Bus1"].bus_type = 'Slack Bus'
circuit1.buses["Bus2"].bus_type = 'PQ Bus'
circuit1.buses["Bus3"].bus_type = 'PQ Bus'
circuit1.buses["Bus4"].bus_type = 'PQ Bus'
circuit1.buses["Bus5"].bus_type = 'PQ Bus'
circuit1.buses["Bus6"].bus_type = 'PQ Bus'
circuit1.buses["Bus7"].bus_type = 'PV Bus' #generator bus type

#circuit1.buses["Bus1"].vpu = 1.0  # Slack bus voltage
#circuit1.buses["Bus1"].delta = 0.0
# circuit1.buses["Bus2"].vpu = 1.0  # PV bus voltage (if it's a PV bus)
#circuit1.buses["Bus7"].vpu = 1.0  # PV bus voltage
#circuit1.buses["Bus7"].real_power = 200

#adding the 2 transformers
circuit1.add_transformer("T1", "Bus1", "Bus2", 125, 8.5, 10 )
circuit1.add_transformer("T2", "Bus6", "Bus7", 200, 10.5, 12 )

#adding the conductor
circuit1.add_conductor("C1",.642, .0217, .385, 460)

#adding the bundle
circuit1.add_bundle("B1",2, 1.5, "C1")

#adding the geometry
circuit1.add_geometry( "G1", 0, 0, 18.5, 0, 37, 0) # ask about how to find x and y values

#adding the 6 transmission lines
circuit1.add_transmission_line("L1", "Bus2", "Bus4", "B1", "C1", "G1", 10)
circuit1.add_transmission_line("L2", "Bus2", "Bus3", "B1", "C1", "G1", 25)
circuit1.add_transmission_line("L3", "Bus3", "Bus5", "B1", "C1", "G1", 20)
circuit1.add_transmission_line("L4", "Bus4", "Bus6", "B1", "C1", "G1", 20)
circuit1.add_transmission_line("L5", "Bus5", "Bus6", "B1", "C1", "G1", 10)
circuit1.add_transmission_line("L6", "Bus4", "Bus5", "B1", "C1", "G1", 35)

#adding the loads
circuit1.add_load("load2", "Bus2", 0, 0)
circuit1.add_load("Load3","Bus3", 110, 50 )
circuit1.add_load("Load4", "Bus4", 100, 70)
circuit1.add_load("Load5", "Bus5", 100, 65)
circuit1.add_load("Load6", "Bus6", 0, 0)
# circuit1.add_load("Load7", "Bus7", 0, 0)

#adding the generators
circuit1.add_generator("G1", "Bus1", 1.0 ,0.0)
circuit1.add_generator("G7", "Bus7", 1.0, 200)

np.set_printoptions(threshold=np.inf, linewidth=np.inf)

circuit1.calc_ybus()
circuit1.print_ybus()

angles = np.array([bus.delta for bus in circuit1.buses.values()])
voltages = np.array([bus.vpu for bus in circuit1.buses.values()])
jacobian = Jacobian(circuit1)

J = jacobian.calc_jacobian(circuit1.buses.values(), circuit1.ybus, angles, voltages)
print("\nJacobian Matrix:")
print(np.round(J,2))

'''
#powerflow = PowerFlow()
#results = powerflow.solve_circuit(circuit1)

# Print results
print("\nPower Flow Solution:")
print("--------------------")
print(f"Converged: {results['converged']}")
print(f"Iterations: {results['iterations']}")

print("\nBus Voltages:")
for i, bus_name in enumerate(circuit1.buses.keys()):
    v_mag = results['v_mag'][i]
    v_ang_deg = np.degrees(results['v_ang'][i])
    print(f"{bus_name}: {v_mag:.4f} ∠{v_ang_deg:.2f}°")

if 'p_calc' in results and 'q_calc' in results:
    print("\nPower Injections:")
    for i, bus_name in enumerate(circuit1.buses.keys()):
        p = results['p_calc'][i]
        q = results['q_calc'][i]
        print(f"{bus_name}: P = {p:.4f} p.u., Q = {q:.4f} p.u.")
'''
solution = Solution("Solution 1", circuit1.buses.values(), circuit1, circuit1.loads)
solution.start()

#print("\nSolution Power Mismatch")
#print(solution.calc_mismatch())
#print("\nPower Injections")
#print(solution.calc_Px())
#print(solution.calc_Qx())

print(f"\nSolution x: {solution.x}")
print(f"\nSolution y: {solution.y}")
print(f"\nSolution Px: {solution.calc_Px()}")
print(f"\nSolution Qx: {solution.calc_Qx()}")
print(f"\nSolution Mismatch: {solution.calc_mismatch()}")
