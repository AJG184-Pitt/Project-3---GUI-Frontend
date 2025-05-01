import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeyEvent

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
    
    # Test case data for seven-bus system - format: (component_type, name, value)
    test_data = [
        # Add buses (with voltage levels in kV)
        ("Bus", "Bus1", "20,Slack Bus"),
        ("Bus", "Bus2", "230,PQ Bus"),
        ("Bus", "Bus3", "230,PQ Bus"),
        ("Bus", "Bus4", "230,PQ Bus"),
        ("Bus", "Bus5", "230,PQ Bus"),
        ("Bus", "Bus6", "230,PQ Bus"),
        ("Bus", "Bus7", "18,PV Bus"),
        
        # Fixed transformer format: from_bus, to_bus, MVA, Z%
        ("Transformer", "T1", "Bus1,Bus2,125,8.5"),
        ("Transformer", "T2", "Bus6,Bus7,200,10.5"),
        
        # Add conductor
        ("Conductor", "C1", "0.642,0.0217,0.385,460"),
        
        # Add bundle
        ("Bundle", "B1", "2,1.5,C1"),
        
        # Add geometry configuration
        ("Geometry", "G1", "0,0,18.5,0,37,0"),
        
        # Add transmission lines to ensure Bus1 has self-admittance
        ("Transmission Line", "L1", "Bus2,Bus4,B1,C1,G1,10"),
        ("Transmission Line", "L2", "Bus2,Bus3,B1,C1,G1,25"),
        ("Transmission Line", "L3", "Bus3,Bus5,B1,C1,G1,20"),
        ("Transmission Line", "L4", "Bus4,Bus6,B1,C1,G1,20"),
        ("Transmission Line", "L5", "Bus5,Bus6,B1,C1,G1,10"),
        ("Transmission Line", "L6", "Bus4,Bus5,B1,C1,G1,35"),
        
        # Add loads
        ("Load", "load2", "Bus2,0,0"),
        ("Load", "Load3", "Bus3,110,50"),
        ("Load", "Load4", "Bus4,100,70"),
        ("Load", "Load5", "Bus5,100,65"),
        ("Load", "Load6", "Bus6,0,0"),
        
        # Add generators with updated format
        ("Generator", "G1", "Bus1,1.0,0.0,0.12,0.14,0.05,0"),
        ("Generator", "G7", "Bus7,1.0,200,0.12,0.14,0.05,0"),
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
    
    # Run the power flow calculation with a longer wait time
    QTest.mouseClick(window.run_button, Qt.MouseButton.LeftButton)
    QTest.qWait(2000)  # Wait longer for simulation to complete
    
    # Keep the application running
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
