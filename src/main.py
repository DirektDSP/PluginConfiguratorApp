import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, QBoxLayout

class ProjectGenerationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PluginTemplate Project Creation")
        self.setGeometry(250, 250, 400, 200)

        # Create a layout for the window
        layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self)
        # layout.

        # Create labels and input fields
        self.label_projectName = QLabel("Project Name:", self)
        self.input_projectName = QLineEdit(self)
        self.label_projectDescription = QLabel("Project Description:", self)
        self.input_projectDescription = QLineEdit(self)
        self.label_author = QLabel("Company:", self)
        self.input_author = QLineEdit(self)

        # Add labels and input fields to the layout
        layout.addWidget(self.label_projectName)
        layout.addWidget(self.input_projectName)
        layout.addWidget(self.label_projectDescription)
        layout.addWidget(self.input_projectDescription)
        layout.addWidget(self.label_author)
        layout.addWidget(self.input_author)

        # JUCE Project related fields

        # Create a button
        self.button = QPushButton("Generate Project", self)
        self.button.clicked.connect(self.generate_project)

        # Add the button to the layout
        layout.addWidget(self.button)

        # Set the layout for the window
        self.setLayout(layout)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def generate_project(self):
        # Add your project generation logic here
        print("Generating project...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectGenerationWindow()
    window.show()
    sys.exit(app.exec())