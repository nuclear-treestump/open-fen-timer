from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPalette, QFont
import time
import constants
import donation_utils

class DonationDisplay(QWidget):

    MAX_VISIBLE_DONATIONS = constants.max_visible_donations  # Set a maximum number of visible donations
    DISPLAY_TIME = constants.donations_display_time
    FADE_TIME = 10  # 10 seconds
    FADE_STEP = 25  # Adjust for faster/slower fade

    def __init__(self, font_name, font_size=48):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.queue = []  # Queue to hold excess donations
        self.active_labels = []  # List to keep track of visible donation labels
        self.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.processing_queue = False
        self.font_size = font_size
        self.font_name = font_name

    def seconds_to_hms(self, seconds):
        """Converts seconds to a HH:MM:SS string."""
        seconds = int(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return h, m, s

    def display_data(self, data):
        """Display data on the screen"""
        donation_type = data.get('donation_type', 'Unknown')
        anonymous = data.get('anonymous', False)
        username = data.get('username', 'Anonymous')
        time_added = int(data.get('time_added', 0.0))
        if data.get('anonymous') is True:
            username = 'Anonymous'
        dis_hours, dis_minutes, dis_seconds = self.seconds_to_hms(seconds=time_added)
        display_message = f"+{dis_hours:02d}:{dis_minutes:02d}:{dis_seconds:02d}"
        self.add_donation(display_message)



    def add_donation(self, display_message):
        if len(self.active_labels) < self.MAX_VISIBLE_DONATIONS:
            self._create_donation_label(display_message)
            QTimer.singleShot(1000 * self.DISPLAY_TIME, self._fade_donation)
        else:
            # If we exceed the maximum visible donations, queue it up.
            self.queue.append(display_message)

    def _create_donation_label(self, display_message):
        donation_label = QLabel(display_message)
        font = QFont(self.font_name, self.font_size)
        donation_label.setFont(font)
        donation_label.setStyleSheet("color: white;")
        self.layout.addWidget(donation_label)
        self.active_labels.append(donation_label)

    def _fade_donation(self):
        if self.active_labels:
            donation_label = self.active_labels[0]  # Get the first (oldest) label

            def step_fade():
                if donation_label not in self.active_labels:
                    fade_timer.stop()
                    return
                current_color = QColor(donation_label.palette().color(QPalette.WindowText))
                if current_color.green() + self.FADE_STEP <= 255:
                    current_color.setGreen(current_color.green() + self.FADE_STEP)
                    donation_label.setStyleSheet(f"color: {current_color.name()};")
                else:
                    donation_label.deleteLater()  # Remove the label after it's fully faded
                    fade_timer.stop()
                    self.active_labels.remove(donation_label)
                    self._process_queue()  # Check the queue

            fade_timer = QTimer(self)
            fade_timer.timeout.connect(step_fade)
            fade_timer.start(round(1000 * self.FADE_TIME / 255 * self.FADE_STEP))  # Calculate interval based on FADE_TIME and FADE_STEP

    def _process_queue(self):
        if not self.processing_queue and self.queue:
            self.processing_queue = True

            def dequeue():
                if self.queue and len(self.active_labels) < self.MAX_VISIBLE_DONATIONS:
                    display_message = self.queue.pop(0)
                    self._create_donation_label(display_message)
                    QTimer.singleShot(1000 * self.DISPLAY_TIME, self._fade_donation)
                    QTimer.singleShot(500, dequeue)  # Add a 500ms delay between dequeuing
                else:
                    self.processing_queue = False

            dequeue()
