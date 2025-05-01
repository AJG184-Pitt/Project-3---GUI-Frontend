# Power Flow Simulation GUI

## Purpose and Scope

The program provides a graphical user interface for power system simulation with a focus on power flow analysis. The program allows users to:

- Model and design power system components (buses, transmission lines, transformers, etc.)
- Perform power flow calculations using numerical methods
- Plot voltage profiles across the system
- Investigate faulted conditions in the power network

The program is designed for educational purposes and small to medium-sized power systems. It employs the Newton-Raphson method for solving nonlinear power flow equations and includes a graphical user interface for building and analyzing power system models.

## Input/Output Structure

### Input Components

The GUI allows the user to add the following power system components:
1. **Bus** - Power system nodes with voltage levels
   - Format: `voltage (kV)` or `voltage (kV),bus_type`
- Example: `138,Slack Bus` or `138,PQ Bus`

2. **Bundle** - Conductor arrangement
   - Format: `number_of_conductors,spacing (ft),conductor_name`
   - Example: `1,0,ACSR336`

3. **Transformer** - Power transformers between buses
   - Format: `from_bus,to_bus,MVA,Z%`
   - Example: `Bus1,Bus2,125,8.5`

4. **Conductor** - Electrical conductors with properties
   - Format: `resistance,reactance,ampacity,diameter`
   - Example: `0.15,0.4,600,0.721`

5. **Geometry** - Physical arrangement of conductors
   - Format: `x1,y1,x2,y2,x3,y3`
- Example: `0,40,10,40,20,40`

6. **Transmission Line** - Power lines connecting buses
   - Format: `from_bus,to_bus,bundle,conductor,geometry,length (mi)`
   - Example: `Bus1,Bus2,Single,ACSR336,FlatHorizontal,10`

7. **Load** - Power consumption
   - Format: `bus,P (MW),Q (MVAR)`
   - Example: `Bus2,20,5`

8. **Generator** - Power generation
   - Format: `bus,Vpu,P (MW)[,xd,xq,xp,ra]`
   - Example: `Bus1,1.05,100,0.12,0.14,0.05,0`

### Output Results

The simulation produces a variety of types of output:

1. **Circuit Elements** - Summary of all elements inserted
2. **Bus Voltages** - Magnitude and angle of voltages at each bus
3. **Power Injections** - Real and reactive power injections at each bus
4. **Mismatch** - final power mismatch indicating solution accuracy
5. **Iterations** - Convergence history and iteration number
6. **Fault Analysis** - Fault current calculation results
7. **Voltage Profile Plot** - Visual representation of system voltages

## How to Run

### Prerequisites

- Python 3.6 or higher
- PyQt6
- NumPy
- Matplotlib

### Installation

1. Install required packages:
```bash
pip install PyQt6 numpy matplotlib
```

2. Download all source files, putting them in the same folder:
   - Core simulation modules: `circuit.py`, `jacobian.py`, `powerflow.py`, `solution.py`, etc.
   - GUI module: `UI.py`
   - Test modules: `UI_testcase.py`, `UI_testcase_2.py`

3. Create an `Assets` folder in the same directory and add a background image named `background.jpg`

### Running the Application

To execute the program with an empty system:
```bash
python UI.py
```

To execute the program with a pre-loaded test case:
```bash
python UI_testcase.py  # For a 3-bus system
```
or
```bash
python UI_testcase_2.py  # For a 7-bus system
```

## How to Test

### Manual Testing

1. Launch the application using `python UI.py`
2. Add components in the proper order:
   - Insert buses first
   - Insert conductors, bundles, and geometries later
- Add transmission lines and transformers
   - Add generators and loads last
3. Click the "Run Simulation" button to execute power flow calculations
4. View results in output text boxes and voltage profile plot

### Automated Testing

There are two automated test scripts included in the repository:

1. **UI_testcase.py** - Constructs and simulates a 3-bus system
   - Includes a slack bus, two load buses
- Adds transmission lines, loads, and a generator
  - Automatically executes the power flow calculation

2. **UI_testcase_2.py** - Creates and simulates a 7-bus system
  - More complex network with transformers and two generators
  - Includes PV and slack buses
  - Automatically executes the power flow calculation

To run these tests:
```bash
python UI_testcase.py
```
or
```bash
python UI_testcase_2.py
```

The tests will populate the system automatically and run the simulation, providing a complete demonstration of the application's functionality.

## Validation and References

### Numerical Method

The Newton-Raphson method is employed for power flow analysis in the app, which is the most widely used method in power system analysis. The implementation follows standard power system engineering practices:
 
1. **Y-bus formation** - Constructs the system admittance matrix
2. **Jacobian calculation** - Develops the linearized system model
3. **Iterative solution** - Solves power flow equations iteratively
4. **Convergence check** - Iterates power mismatches until convergence

### Test Cases

The following test cases are included to validate the application:

1. **3-bus system** - Simple radial network with conservative values
   for numerical stability
2. **7-bus system** - More complex meshed network with transformers and multiple generators

### References

1. Grainger, J.J. and Stevenson, W.D., "Power System Analysis", McGraw-Hill, 1994.
2. Arrillaga, J. and Watson, N.R., "Computer Modelling of Electrical Power Systems", Wiley, 2001.
3. Milano, F., "Power System Modelling and Scripting", Springer, 2010.
4. Glover, J.D., Sarma, M.S., and Overbye, T.J., "Power System Analysis and Design", Cengage Learning, 2016.

### Limitations

- The program is intended for educational use and may not be adequate for very large systems
- The fault analysis is idealized and does not cover all real-life considerations
- GUI response will be slower for larger systems due to matrix calculations

## Future Enhancements

- Add the facility to import/export power system data from standard formats (e.g., IEEE CDF)
- Add dynamic simulation capability
- Extend fault analysis with detailed models
- Add economic dispatch and optimal power flow capability
- Improve visualization with interactive one-line diagrams
