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
    
    # Test case data - format: (component_type, name, value)
    test_data = [
        # Add buses (voltage level in kV)
        ("Bus", "Bus1", "138,Slack Bus"),
        ("Bus", "Bus2", "138,PQ Bus"),
        ("Bus", "Bus3", "138,PQ Bus"),
        
        # Add conductors
        ("Conductor", "ACSR336", "0.0306,0.1273,600,0.721"),
        
        # Add bundles
        ("Bundle", "Single", "1,0,ACSR336"),
        
        # Add geometry configuration
        ("Geometry", "FlatHorizontal", "0,40,10,40,20,40"),
        
        # Add transmission lines
        ("Transmission Line", "Line1", "Bus1,Bus2,Single,ACSR336,FlatHorizontal,50"),
        ("Transmission Line", "Line2", "Bus2,Bus3,Single,ACSR336,FlatHorizontal,50"),
        
        # Add loads
        ("Load", "Load2", "Bus2,100,20"),
        ("Load", "Load3", "Bus3,150,30"),
        
        # Add generator
        ("Generator", "Gen1", "Bus1,1.05,300"),
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
    
    # Run the simulation
    QTest.mouseClick(window.run_button, Qt.MouseButton.LeftButton)
    QTest.qWait(1000)  # Wait for simulation to complete
    
    # Keep the application running
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
