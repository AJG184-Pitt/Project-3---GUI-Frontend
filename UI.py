from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

# Import circuit simulation modules
from circuit import Circuit
from jacobian import Jacobian
from powerflow import PowerFlow
from solution import Solution
from load import Load
from solution_symmetric import Solution_Faults
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window title and size constraints
        self.setWindowTitle("PyQt6 GUI for Powerflow Simulation")
        self.setFixedSize(1280, 720)

        # Initialize circuit
        self.circuit = Circuit("Circuit Simulation")
        
        # Create central widget and layout
        central_widget = QWidget()
        central_widget.setStyleSheet(f"""
            QWidget {{
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)

        # Create and configure the QComboBox
        self.combo_box = QComboBox()  # Instantiate QComboBox
        options = ['Bus', 'Bundle', 'Transformer', 'Conductor', 'Geometry', 'Transmission Line', 'Load', 'Generator']
        self.combo_box.addItems(options)  # Use addItems on QComboBox
        self.combo_box.setFixedWidth(200)
        self.combo_box.setFixedHeight(50)
        self.combo_box.currentIndexChanged.connect(self.update_value_field_placeholder)

        # Text box for entering object name
        self.text_name = QLineEdit(central_widget)
        self.text_name.setFixedWidth(200)
        self.text_name.setFixedHeight(50)
        self.text_name.setPlaceholderText("Enter Name here...")

        self.text_value = QLineEdit(central_widget)
        self.text_value.setFixedWidth(200)
        self.text_value.setFixedHeight(50)
        self.text_value.setPlaceholderText("Enter Value here...")

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_object)

        # Status label
        self.status_label = QLabel()
        self.status_label.setFixedWidth(400)
        self.status_label.setFixedHeight(50)

        # Run simulation button
        self.run_button = QPushButton('Run Simulation')
        self.run_button.clicked.connect(self.run_simulation)
        self.run_button.setFixedWidth(200)
        self.run_button.setFixedHeight(50)

        self.output1 = QTextEdit(central_widget)
        self.output1.setFixedWidth(200)
        self.output1.setFixedHeight(100)
        self.output1.setPlaceholderText("Circuit Elements")

        self.output2 = QTextEdit(central_widget)
        self.output2.setFixedWidth(200)
        self.output2.setFixedHeight(100)
        self.output2.setPlaceholderText("Bus Voltages")

        self.output3 = QTextEdit(central_widget)
        self.output3.setFixedWidth(200)
        self.output3.setFixedHeight(100)
        self.output3.setPlaceholderText("Power Injections")

        self.output4 = QTextEdit(central_widget)
        self.output4.setFixedWidth(200)
        self.output4.setFixedHeight(100)
        self.output4.setPlaceholderText("Mismatch")

        self.output5 = QTextEdit(central_widget)
        self.output5.setFixedWidth(200)
        self.output5.setFixedHeight(100)
        self.output5.setPlaceholderText("Iterations")

        self.output6 = QTextEdit(central_widget)
        self.output6.setFixedWidth(200)
        self.output6.setFixedHeight(100)
        self.output6.setPlaceholderText("Fault Analysis")

        # Blank object
        for i in range(36):
            blank_label = f'blank{i}'
            setattr(self, blank_label, QLabel())
            blank_label = getattr(self, blank_label)
            blank_label.setFixedWidth(200)
            blank_label.setFixedHeight(50)

        for i in range(6):
            for j in range(6):
                index = i * 6 + j
                grid.addWidget(getattr(self, f'blank{index}'), i, j)

        # Add the widgets to the layout
        grid.addWidget(self.combo_box, 2, 0)
        grid.addWidget(self.text_name, 2, 1)
        grid.addWidget(self.text_value, 2, 2)
        grid.addWidget(self.add_button, 3, 1)
        grid.addWidget(self.run_button, 3, 0)
        grid.addWidget(self.status_label, 3, 2)

        # Output textbox fields
        grid.addWidget(self.output1, 1, 4)
        grid.addWidget(self.output2, 2, 4)
        grid.addWidget(self.output3, 3, 4)
        grid.addWidget(self.output4, 4, 4)
        grid.addWidget(self.output5, 5, 4)
        grid.addWidget(self.output6, 6, 4)

        # First, set all output text boxes to read-only and disable focus
        self.output1.setReadOnly(True)
        self.output1.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output2.setReadOnly(True)
        self.output2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output3.setReadOnly(True)
        self.output3.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output4.setReadOnly(True)
        self.output4.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output5.setReadOnly(True)
        self.output5.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output6.setReadOnly(True)
        self.output6.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Set explicit tab order for focusable elements
        self.combo_box.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_name.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_value.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.add_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.run_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set up explicit tab order
        self.setTabOrder(self.combo_box, self.text_name)
        self.setTabOrder(self.text_name, self.text_value)
        self.setTabOrder(self.text_value, self.add_button)
        self.setTabOrder(self.add_button, self.run_button)
        self.setTabOrder(self.run_button, self.combo_box)  # Cycle back to start
        
        # Initialize additional component fields
        self.additional_fields = {}
        self.update_value_field_placeholder()
        
        # Store circuit elements by type for tracking
        self.circuit_elements = {
            'Bus': [],
            'Bundle': [],
            'Transformer': [],
            'Conductor': [],
            'Geometry': [],
            'Transmission Line': [],
            'Load': [],
            'Generator': []
        }
        
        # Update circuit elements display
        self.update_circuit_elements_display()

    def update_value_field_placeholder(self):
        """Update the placeholder text based on the selected component type"""
        component_type = self.combo_box.currentText()
        
        placeholders = {
            'Bus': "Enter voltage level (kV)",
            'Bundle': "Enter # conductors, spacing (ft)",
            'Transformer': "Enter MVA, Z% (X/R = 10)",
            'Conductor': "Enter ACSR code or resistance",
            'Geometry': "Enter coordinates (x1,y1,x2,y2,x3,y3)",
            'Transmission Line': "Enter from_bus, to_bus, length (mi)",
            'Load': "Enter P (MW), Q (MVAR)",
            'Generator': "Enter Vpu, P (MW)"
        }
        
        self.text_value.setPlaceholderText(placeholders.get(component_type, "Enter Value here..."))

    def add_object(self):
        """Add a component to the circuit based on user selection"""
        selected_option = self.combo_box.currentText()
        name = self.text_name.text().strip()
        value = self.text_value.text().strip()

        if not name or not value:
            self.status_label.setText("Name and Value fields must be filled!")
            return
        
        try:
            # Process addition based on component type
            if selected_option == "Bus":
                # Expected value: voltage level in kV
                values = value.split(',')
                voltage = float(values[0])
                
                # Set bus type if provided, default to PQ Bus
                bus_type = values[1] if len(values) > 1 else 'PQ Bus'
                
                self.circuit.add_bus(name, voltage)
                self.circuit.buses[name].bus_type = bus_type
                
                self.circuit_elements['Bus'].append(f"{name} ({voltage} kV, {bus_type})")

                if bus_type == 'Slack Bus' or bus_type == 'PV Bus':
                    self.circuit.buses[name].vpu = 1.0
                    self.circuit.buses[name].delta = 0.0
                
            elif selected_option == "Bundle":
                # Expected value: "num_conductors,spacing,conductor_name"
                values = value.split(',')
                if len(values) != 3:
                    raise ValueError("Bundle needs # conductors, spacing, and conductor name separated by commas")
                num_conductors = int(values[0])
                spacing = float(values[1])
                conductor_type = values[2]
                self.circuit.add_bundle(name, num_conductors, spacing, conductor_type)
                self.circuit_elements['Bundle'].append(f"{name} ({num_conductors} @ {spacing}ft, {conductor_type})")
                
            elif selected_option == "Transformer":
                # Expected value: "from_bus,to_bus,MVA,Zpct"
                values = value.split(',')
                if len(values) != 4:
                    raise ValueError("Transformer needs from_bus, to_bus, MVA, Z% separated by commas")
                from_bus = values[0]
                to_bus = values[1]
                mva = float(values[2])
                zpct = float(values[3])
                x_r = 10  # Default X/R ratio
                self.circuit.add_transformer(name, from_bus, to_bus, mva, zpct, x_r)
                self.circuit_elements['Transformer'].append(f"{name} ({from_bus}-{to_bus}, {mva} MVA)")
                
            elif selected_option == "Conductor":
                # Expected value: "resistance,reactance,ampacity,diameter"
                values = value.split(',')
                if len(values) != 4:
                    raise ValueError("Conductor needs resistance, reactance, ampacity, diameter separated by commas")
                resistance = float(values[0])
                reactance = float(values[1])
                ampacity = float(values[2])
                diameter = float(values[3])
                self.circuit.add_conductor(name, resistance, reactance, ampacity, diameter)
                self.circuit_elements['Conductor'].append(f"{name} ({ampacity} A)")
                
            elif selected_option == "Geometry":
                # Expected value: "x1,y1,x2,y2,x3,y3"
                values = value.split(',')
                if len(values) != 6:
                    raise ValueError("Geometry needs six coordinates: x1,y1,x2,y2,x3,y3")
                x1, y1, x2, y2, x3, y3 = map(float, values)
                self.circuit.add_geometry(name, x1, y1, x2, y2, x3, y3)
                self.circuit_elements['Geometry'].append(f"{name}")
                
            elif selected_option == "Transmission Line":
                # Expected value: "from_bus,to_bus,bundle,conductor,geometry,length"
                values = value.split(',')
                if len(values) != 6:
                    raise ValueError("Line needs from_bus,to_bus,bundle,conductor,geometry,length(mi)")
                from_bus = values[0]
                to_bus = values[1]
                bundle = values[2]
                conductor = values[3]
                geometry = values[4]
                length = float(values[5])
                self.circuit.add_transmission_line(name, from_bus, to_bus, bundle, conductor, geometry, length)
                self.circuit_elements['Transmission Line'].append(f"{name} ({from_bus}-{to_bus}, {length}mi)")
                
            elif selected_option == "Load":
                # Expected value: "bus,p_mw,q_mvar"
                values = value.split(',')
                if len(values) != 3:
                    raise ValueError("Load needs bus,p_mw,q_mvar")
                bus = values[0]
                p_mw = float(values[1])
                q_mvar = float(values[2])
                self.circuit.add_load(name, bus, p_mw, q_mvar)
                self.circuit_elements['Load'].append(f"{name} ({bus}, {p_mw}MW, {q_mvar}MVAR)")
                
            elif selected_option == "Generator":
                # Expected value: "bus,vpu,p_mw,xd,xq,xp,ra"
                values = value.split(',')
                if len(values) < 3:
                    raise ValueError("Generator needs bus,vpu,p_mw[,xd,xq,xp,ra]")
                bus = values[0]
                vpu = float(values[1])
                p_mw = float(values[2])
                
                # Optional impedance parameters with defaults
                xd = float(values[3]) if len(values) > 3 else 0.12
                xq = float(values[4]) if len(values) > 4 else 0.14
                xp = float(values[5]) if len(values) > 5 else 0.05
                ra = float(values[6]) if len(values) > 6 else 0
                
                self.circuit.add_generator(name, bus, vpu, p_mw, xd, xq, xp, ra)
                self.circuit_elements['Generator'].append(f"{name} ({bus}, {p_mw}MW)")
            
            message = f"Added {selected_option}: {name} with value={value}"
            print(message)
            self.status_label.setText(message)
            
            # Update circuit elements display
            self.update_circuit_elements_display()
            
            # Clear fields after adding
            self.text_name.clear()
            self.text_value.clear()
            self.combo_box.setFocus()  # Return focus to the first input
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            print(f"Error adding {selected_option}: {str(e)}")

    def update_circuit_elements_display(self):
        """Update the display of circuit elements in output1"""
        elements_text = "Circuit Elements:\n\n"
        
        for category, items in self.circuit_elements.items():
            if items:
                elements_text += f"{category}:\n"
                for item in items:
                    elements_text += f"  - {item}\n"
                elements_text += "\n"
        
        self.output1.setText(elements_text)

    def run_simulation(self):
        """Run the powerflow simulation on the current circuit"""
        try:
            self.status_label.setText("Running simulation...")
            
            # Debug: Print bus information
            print("Bus information before simulation:")
            for name, bus in self.circuit.buses.items():
                print(f"Bus {name}: type={bus.bus_type}, vpu={getattr(bus, 'vpu', 'N/A')}, delta={getattr(bus, 'delta', 'N/A')}")

            if "Bus1" in self.circuit.buses:
                self.circuit.buses["Bus1"].bus_type = 'Slack Bus'
                print("Set Bus1 as Slack Bus")
            
            # Calculate Y-bus matrix
            self.circuit.calc_ybus()
            
            # Initialize powerflow and run solution
            powerflow = PowerFlow(self.circuit)
            
            # Debug: Print additional info
            print("Number of buses:", len(self.circuit.buses))
            print("Bus types:", [bus.bus_type for bus in self.circuit.buses.values()])
            
            results = powerflow.solve_circuit(self.circuit)
            
            # Update the output windows with results
            self.update_simulation_results(results)
            
            # If there are sufficient buses, run fault analysis
            if len(self.circuit.buses) > 0:
                self.run_fault_analysis()
            
            self.status_label.setText("Simulation completed successfully")
            
        except Exception as e:
            self.status_label.setText(f"Simulation error: {str(e)}")
            print(f"Error running simulation: {str(e)}")
            # Print the full traceback for debugging
            import traceback
            traceback.print_exc()

    def update_simulation_results(self, results):
        """Update the output text fields with simulation results"""
        # Output 2: Bus Voltages
        voltage_text = "Bus Voltages:\n\n"
        for i, (bus_name, bus) in enumerate(self.circuit.buses.items()):
            if i < len(results['v_mag']) and i < len(results['v_ang']):
                v_mag = results['v_mag'][i]
                v_ang_deg = np.degrees(results['v_ang'][i])
                voltage_text += f"{bus_name}: {v_mag:.4f} ∠{v_ang_deg:.2f}°\n"
        self.output2.setText(voltage_text)
        
        # Output 3: Power Injections
        power_text = "Power Injections:\n\n"
        if 'p_calc' in results and 'q_calc' in results:
            for i, (bus_name, bus) in enumerate(self.circuit.buses.items()):
                if i < len(results['p_calc']) and i < len(results['q_calc']):
                    p = results['p_calc'][i]
                    q = results['q_calc'][i]
                    power_text += f"{bus_name}: P = {p:.4f} p.u., Q = {q:.4f} p.u.\n"
        self.output3.setText(power_text)
        
        # Output 4: Mismatch
        mismatch_text = "Final Mismatch:\n\n"
        mismatch_text += f"Maximum Mismatch: {results['final_mismatch']:.6f}\n"
        self.output4.setText(mismatch_text)
        
        # Output 5: Iterations
        iteration_text = "Convergence History:\n\n"
        iteration_text += f"Converged: {results['converged']}\n"
        iteration_text += f"Iterations: {results['iterations']}\n\n"
        if len(results['mismatch_history']) > 0:
            for i, mismatch in enumerate(results['mismatch_history']):
                iteration_text += f"Iter {i+1}: Mismatch = {mismatch:.6f}\n"
        else:
            iteration_text += "No iterations performed\n"
        self.output5.setText(iteration_text)

    def run_fault_analysis(self):
        """Run fault analysis and display results"""
        try:
            fault_text = "Fault Analysis:\n\n"
            
            # Select first bus as example fault location
            fault_bus_name = next(iter(self.circuit.buses))
            fault_bus = self.circuit.buses[fault_bus_name]
            
            # Run fault analysis
            faults = Solution_Faults(self.circuit)
            fault_results = faults.calculate_fault_currents_2(fault_bus)
            
            # Display results
            fault_text += f"Fault at {fault_bus_name}:\n"
            fault_text += f"Fault Current: {abs(fault_results[0]):.4f} pu\n\n"
            
            # Show voltage drops at each bus during fault
            fault_text += "Bus Voltages During Fault:\n"
            for i, (bus_name, bus) in enumerate(self.circuit.buses.items()):
                if i < len(fault_results[1]):
                    fault_text += f"{bus_name}: {abs(fault_results[1][i]):.4f} pu\n"
                    
            self.output6.setText(fault_text)
            
        except Exception as e:
            self.output6.setText(f"Fault analysis error: {str(e)}")
            print(f"Error running fault analysis: {str(e)}")


def main():
    app = QApplication([])  # Pass an empty list to QApplication
    window = MainWindow()
    window.show()

    app.exec()

if __name__ == '__main__':
    main()
