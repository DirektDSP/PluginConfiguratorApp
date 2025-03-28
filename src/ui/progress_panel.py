from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QTextEdit, 
    QProgressBar, QHBoxLayout, QCheckBox
)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QTextCursor

class ProgressPanel(QWidget):
    """Panel for displaying progress and logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize UI components"""
        self.layout = QVBoxLayout(self)
        
        # Group box
        self.group_box = QGroupBox("Progress")
        self.group_layout = QVBoxLayout()
        
        # Add toggle for log visibility
        self.header_layout = QHBoxLayout()
        self.show_log_checkbox = QCheckBox("Show Log")
        self.show_log_checkbox.setChecked(True)
        self.header_layout.addWidget(self.show_log_checkbox)
        self.header_layout.addStretch()
        self.group_layout.addLayout(self.header_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        self.log_text.setPlaceholderText("Operation logs will appear here...")
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.group_layout.addWidget(self.log_text)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_layout.addWidget(self.progress_bar)
        
        # Connect toggle checkbox
        self.show_log_checkbox.toggled.connect(self.log_text.setVisible)
        
        # Set layout for group box
        self.group_box.setLayout(self.group_layout)
        
        # Add group box to main layout
        self.layout.addWidget(self.group_box)
    
    @Slot(str)
    def log_message(self, message):
        """Add a message to the log"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    @Slot(int)
    def update_progress(self, value):
        """Update the progress bar value"""
        self.progress_bar.setValue(value)
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.clear()
    
    def reset_progress(self):
        """Reset the progress bar to zero"""
        self.progress_bar.setValue(0)
