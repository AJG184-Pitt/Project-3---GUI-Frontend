from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget, QTextEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set window title and size constraints
        self.setWindowTitle("PyQt6 GUI for Powerflow Simulation")
        self.setFixedSize(1280, 720)

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
        options = ['Bus', 'Bundle', 'Transformer']
        self.combo_box.addItems(options)  # Use addItems on QComboBox
        self.combo_box.setFixedWidth(200)
        self.combo_box.setFixedHeight(50)

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

        # Status label - was missing in your original code
        self.status_label = QLabel()
        self.status_label.setFixedWidth(400)
        self.status_label.setFixedHeight(50)

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
        grid.addWidget(self.status_label, 3, 2)

        # Set explicit tab order for focusable elements
        self.combo_box.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_name.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_value.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.add_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set up explicit tab order
        self.setTabOrder(self.combo_box, self.text_name)
        self.setTabOrder(self.text_name, self.text_value)
        self.setTabOrder(self.text_value, self.add_button)
        self.setTabOrder(self.add_button, self.combo_box)  # Cycle back to start


    def add_object(self):
        selected_option = self.combo_box.currentText()
        name = self.text_name.text().strip()
        value = self.text_value.text().strip()

        if not name or not value:
            self.status_label.setText("Name and Value fields must be filled!")
            return
        
        message = f"Added {selected_option}: Name={name}, Value={value}"
        print(message)
        self.status_label.setText(message)
        
        # Clear fields after adding
        self.text_name.clear()
        self.text_value.clear()
        self.combo_box.setFocus()  # Return focus to the first input


def main():
    app = QApplication([])  # Pass an empty list to QApplication
    window = MainWindow()
    window.show()

    app.exec()

if __name__ == '__main__':
    main()
