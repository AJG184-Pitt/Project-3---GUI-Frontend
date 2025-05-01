import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeyEvent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("power_system_test.log"),
        logging.StreamHandler()
    ]
)

# Import the main window class from your application
from UI import MainWindow

def main():
    # Create the Qt Application
    app = QApplication(sys.argv)
    
    # Create the main window
    window = MainWindow()
    window.show()
    
    # Wait for the UI to load
    QTest.qWait(500)
    
    # Test case data with even more conservative values for better convergence
    test_data = [
        # Add buses (voltage level in kV)
        ("Bus", "Bus1", "138,Slack Bus"),
        ("Bus", "Bus2", "138,PQ Bus"),
        ("Bus", "Bus3", "138,PQ Bus"),
        
        # Add conductor with much higher impedance for numerical stability
        ("Conductor", "ACSR336", "0.15,0.4,600,0.721"),
        
        # Add bundles
        ("Bundle", "Single", "1,0,ACSR336"),
        
        # Add geometry configuration
        ("Geometry", "FlatHorizontal", "0,40,10,40,20,40"),
        
        # Add shorter transmission lines
        ("Transmission Line", "Line1", "Bus1,Bus2,Single,ACSR336,FlatHorizontal,10"),
        ("Transmission Line", "Line2", "Bus2,Bus3,Single,ACSR336,FlatHorizontal,10"),
        
        # Add much smaller loads
        ("Load", "Load2", "Bus2,20,5"),
        ("Load", "Load3", "Bus3,25,8"),
        
        # Add generator with higher voltage setpoint
        ("Generator", "Gen1", "Bus1,1.05,100,0.12,0.14,0.05,0"),
    ]
    
    # Function to set combo box selection
    def select_component(component_type):
        index = window.combo_box.findText(component_type)
        window.combo_box.setCurrentIndex(index)
        QTest.qWait(100)
    
    # Run through test data
    for component_type, name, value in test_data:
        # Select component type
        select_component(component_type)
        
        # Enter name
        window.text_name.clear()
        QTest.keyClicks(window.text_name, name)
        QTest.qWait(100)
        
        # Enter value
        window.text_value.clear()
        QTest.keyClicks(window.text_value, value)
        QTest.qWait(100)
        
        # Click add button
        QTest.mouseClick(window.add_button, Qt.MouseButton.LeftButton)
        QTest.qWait(300)  # Wait longer after adding to see status updates
        
        # Log the component addition
        logging.info(f"Added {component_type}: {name} with value={value}")
    
    # Print system summary before running simulation
    logging.info("\n===== SYSTEM SUMMARY BEFORE SIMULATION =====")
    
    # Get the number of each component type
    try:
        logging.info(f"Number of buses: {len(window.circuit.buses)}")
        logging.info(f"Number of transmission lines: {len(window.circuit.transmission_lines)}")
        logging.info(f"Number of transformers: {len(window.circuit.transformers)}")
        logging.info(f"Number of loads: {len(window.circuit.loads)}")
        logging.info(f"Number of generators: {len(window.circuit.generators)}")
    except AttributeError as e:
        logging.error(f"Error accessing circuit components: {e}")
    
    # Try to set better initial conditions if possible
    try:
        # Access circuit object to set initial conditions
        for bus_name, bus in window.circuit.buses.items():
            if bus.bus_type == "Slack Bus":
                bus.vpu = 1.05  # Higher voltage for slack bus
                bus.delta = 0.0
                logging.info(f"Set initial conditions for {bus_name}: V={bus.vpu}pu, delta={bus.delta}°")
    except Exception as e:
        logging.error(f"Error setting initial conditions: {e}")
    
    # Run the simulation with even longer wait time
    logging.info("\n===== RUNNING SIMULATION =====")
    QTest.mouseClick(window.run_button, Qt.MouseButton.LeftButton)
    QTest.qWait(3000)  # Wait longer for simulation to complete
    
    # Print simulation results
    logging.info("\n===== SIMULATION RESULTS =====")
    
    # Try to find convergence info in text widgets
    try:
        for widget_name in ['results_text_edit', 'text_results', 'log_text', 'output_text']:
            if hasattr(window, widget_name):
                results_text = getattr(window, widget_name).toPlainText()
                logging.info(f"Results from {widget_name}:\n{results_text}")
                if "converged" in results_text.lower():
                    convergence_line = [line for line in results_text.split('\n') if "converged" in line.lower()]
                    logging.info(f"Convergence info: {convergence_line}")
    except Exception as e:
        logging.error(f"Error accessing text widgets: {e}")
    
    # Check status label
    try:
        if hasattr(window, 'status_label'):
            status_text = window.status_label.text()
            logging.info(f"Status: {status_text}")
    except Exception as e:
        logging.error(f"Error accessing status label: {e}")
    
    # Keep the application running
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
