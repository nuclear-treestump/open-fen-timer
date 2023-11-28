# elapsed_timer.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt

class ElapsedTimer(QWidget):
    def __init__(self, initial_time=0, font_color="white", font_name="Arial", font_size=24, bg_color="green"):
        super().__init__()

        # Initialize the total_seconds with the given initial_time
        self.total_seconds = initial_time
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color

        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_time_to_file)
        self.save_timer.start(600000)
        
        self.initUI()
        self.start_updating()

    def get_seconds(self):
        return self.total_seconds

    def initUI(self):
        # Create a QVBoxLayout for the widget
        self.layout = QVBoxLayout()

        # QLabel to display the total elapsed time
        self.label = QLabel(self.seconds_to_hms(self.total_seconds))
        self.label.setAlignment(Qt.AlignCenter)
        
        # Set font for the label
        self.label.setFont(QFont(self.font_name, self.font_size))

        self.label.setStyleSheet(f"color: {self.font_color};")
        self.setStyleSheet(f"background-color: {self.bg_color};")
        
        # Add label to layout
        self.layout.addWidget(self.label)
        
        # Set layout for the widget
        self.setLayout(self.layout)

    def seconds_to_hms(self, seconds):
        """Converts seconds to a HH:MM:SS string."""
        m, s = divmod(seconds, 60)

        return f"{m:02d}min"

    def update_display(self):
        """Updates the QLabel with the current total_seconds."""
        self.label.setText(self.seconds_to_hms(self.total_seconds))

    def add_seconds(self, seconds):
        """Adds seconds to the total_seconds."""
        self.total_seconds += seconds
        self.update_display()

    def start_updating(self):
        # QTimer to periodically update the display
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second

    def save_time_to_file(self):
        with open('current.lock', 'w') as file:
            file.write(str(self.total_seconds))

    def closeEvent(self, event):
        self.save_time_to_file()
        super().closeEvent(event)
