import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import constants
import logging
from donation_display import DonationDisplay
from elapsed_timer import ElapsedTimer
import threading
from flask_server import run_flask_app, shared_queue

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='timer.log', 
                    filemode='w')

logger = logging.getLogger(__name__)

logger.debug("Test Debug message")
logger.info("Test Informational message")
logger.warning("Test Warning message")
logger.error("Test Error message")
logger.critical("Test Critical error message")

def load_total_time_added():
    try:
        with open('current.lock', 'r') as file:
            return int(file.read().strip())
    except (IOError, ValueError):
        return 0
    
TOTAL_TIME_ADDED = load_total_time_added()


class TimerDisplay(QWidget):

    COLOR_SHORTCUTS = {
        'rgb_green': '#00FF00',
        'rgb_red': '#FF0000',
        'rgb_blue': '#0000FF',
        # add more shortcuts if necessary
    }
    def __init__(self, hours, minutes, seconds, font_name="Arial", font_size=48, font_color="white", bg_color="green"):
        super().__init__()

        # Convert everything to seconds for internal tracking
        self.remaining_seconds = hours * 3600 + minutes * 60 + seconds
        self.paused = False
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color

        self.initUI()
        self.pause_timer()
        
    def initUI(self):
        # Create a container for the timer and the PAUSED labels
        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)

        # Timer label
        self.timer_label = QLabel(self.seconds_to_hms(self.remaining_seconds))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.container_layout.addWidget(self.timer_label)

        # Paused label
        self.paused_label = QLabel("PAUSED") # UNTIL 1 SEP 00:01")
        self.paused_label.setAlignment(Qt.AlignCenter)
        self.paused_label.hide()  # Initially hidden
        self.container_layout.addWidget(self.paused_label)

        self.time_out_label = QLabel("LOCKED")
        self.time_out_label.setAlignment(Qt.AlignCenter)
        self.time_out_label.hide()
        self.container_layout.addWidget(self.time_out_label)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.container)

        # Test and Pause buttons
        self.test_button = QPushButton('Test', self)
        self.pause_button = QPushButton('Pause', self)
        self.pause_button.setVisible(False)  # Initially hidden

        # Connect the test button to the method to toggle the pause button's visibility
        self.test_button.clicked.connect(self.toggle_pause_button)
        self.pause_button.clicked.connect(self.toggle_pause)

        # Add the buttons to the layout
        self.layout.addWidget(self.test_button)
        self.layout.addWidget(self.pause_button)

        # Settings and styling
        self.update_font()
        self.update_background()
        self.main_timer = QTimer(self)
        self.main_timer.timeout.connect(self.decrement)
        self.main_timer.start(1000)  # Start the timer, it'll call decrement() every second

        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_paused_label_color)

        self.setLayout(self.layout)

        # Button to add 30 seconds
        self.add_30s_button = QPushButton('+30s', self)
        self.add_30s_button.clicked.connect(lambda: self.add_seconds(30))
        self.layout.addWidget(self.add_30s_button)

        # Button to add 300 seconds
        self.add_300s_button = QPushButton('+300s', self)
        self.add_300s_button.clicked.connect(lambda: self.add_seconds(300))
        self.layout.addWidget(self.add_300s_button)

        # Button to add 1 hour
        self.add_1h_button = QPushButton('+1h', self)
        self.add_1h_button.clicked.connect(lambda: self.add_hours(1))
        self.layout.addWidget(self.add_1h_button)



    # ... [Same methods for font, background and updates as above] ...

    def toggle_paused_label_color(self):
        current_color = self.paused_label.styleSheet()
        if constants.PAUSE_COLOR in current_color:
            self.paused_label.setStyleSheet(f"color: {self.bg_color};")
        else:
            self.paused_label.setStyleSheet(f"color: {constants.PAUSE_COLOR};")

    def seconds_to_hms(self, seconds):
        """Converts seconds to a HH:MM:SS string."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"--{h:02d}:{m:02d}:{s:02d}--"

    def decrement(self):
        """Decrements the timer by one second and updates the display."""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.timer_label.setText(self.seconds_to_hms(self.remaining_seconds))
            if self.remaining_seconds <= 0:
                print("ITS OVER!!!!")
                pass

    def add_seconds(self, seconds):
        """Adds a certain number of seconds to the timer."""
        self.remaining_seconds += seconds
        elapsed_time_window.add_seconds(seconds)
        self.timer_label.setText(self.seconds_to_hms(self.remaining_seconds))

    def add_hours(self, hours):
        """Adds a certain number of hours to the timer."""
        self.add_seconds(hours * 3600)

    def update_font(self):
        """Updates the timer's font based on attributes."""
        self.timer_font = QFont(self.font_name, self.font_size)
        self.timer_label.setFont(self.timer_font)
        self.timer_label.setStyleSheet(f"color: {self.font_color};")
        
        # Apply the same styles to the paused label
        pause_font_size = (int(self.font_size))
        self.paused_font = QFont(self.font_name, (int(self.font_size)))
        self.paused_label.setFont(self.paused_font)
        self.paused_label.setStyleSheet(f"color: {constants.PAUSE_COLOR};")

        # Apply the same styles to the locked label
        pause_font_size = (int(self.font_size))
        self.locked_font = QFont(self.font_name, (int(self.font_size)))
        self.time_out_label.setFont(self.paused_font)
        self.time_out_label.setStyleSheet(f"color: {constants.PAUSE_COLOR};")

    def resolve_color(self, color_name):
        """Resolve color shortcut to its actual value."""
        return self.COLOR_SHORTCUTS.get(color_name, color_name)
    
    def update_background(self):
        """Updates the timer's background based on attributes."""
        resolved_color = self.resolve_color(self.bg_color)
        self.setStyleSheet(f"background-color: {resolved_color};")

    def toggle_pause(self):
        """Toggle the timer between paused and running."""
        if self.paused:
            self.paused = False
            self.paused_label.hide()
            self.blink_timer.stop()
            self.timer_label.show()
            self.main_timer.start(1000)
        else:
            self.paused = True
            self.paused_label.show()
            self.blink_timer.start(1000)
            self.paused_label.raise_()
            self.main_timer.stop()

    def pause_timer(self):
        if not self.paused:
            self.paused = True
            self.paused_label.show()
            self.blink_timer.start(1000)
            self.paused_label.raise_()  # Raise the paused label to the front
            self.main_timer.stop()  # Pause the main timer

    def play_timer(self):
        if self.paused:
            self.paused = False
            self.paused_label.hide()
            self.blink_timer.stop()
            self.timer_label.show()
            self.main_timer.start(1000)  # Resume the main timer

    def toggle_pause_button(self):
        # Toggle the visibility of the pause button
        self.pause_button.setVisible(not self.pause_button.isVisible())

    def check_queue(self):
        current_time = self.remaining_seconds
        total_time = elapsed_time_window.get_seconds()
        max_time = constants.MAX_TIME
        print(total_time)
        print(current_time)
        if int(max_time) > int(total_time):
            while not shared_queue.empty():
                donation_data = shared_queue.get()
                print("DATA RECEIVED")
                print(donation_data)
                if donation_data["donation_type"] == "chatctrl":
                    print("Received C2 Command. Parsing..")
                    if (donation_data["action"].lower()) == "pause":
                        print("Pausing Timer")
                        self.pause_timer()
                        return
                    elif (donation_data["action"].lower()) == "play":
                        print("Resuming Timer")
                        self.play_timer()
                        return
                elif (donation_data["donation_type"] == "chatcmd" or donation_data["donation_type"] == "streamlabs" or donation_data["donation_type"] == "patreon"):
                    print("Received chatcmd donation")
                    self.add_seconds(int(donation_data["time_added"]))
                    donation_window.display_data(data=donation_data)
                    return
                elif (donation_data["donation_type"] == "bits" or donation_data["donation_type"] == "sub" or donation_data["donation_type"] == "giftsub" or donation_data["donation_type"] == "masssub"):
                    print("Received bits or sub donation")
                    self.add_seconds(int(donation_data["time_added"]))
                    donation_window.display_data(data=donation_data)
                    return
        elif int(max_time) <= int(total_time):
            print("DONATION NOT ACCEPTED. TIME OUT.")
            self.time_out_label.show()




# For testing
if __name__ == "__main__":
    print(constants.ASCII_DATA)
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    app = QApplication(sys.argv)
    
    # Your TimerDisplay Window
    window = TimerDisplay(font_name=constants.FONT_NAME, font_size=constants.FONT_SIZE, bg_color=constants.BG_COLOR, hours=constants.START_HOURS, minutes=constants.START_MINUTES, seconds=constants.START_SECONDS)
    queue_timer = QTimer()
    queue_timer.timeout.connect(window.check_queue)
    queue_timer.start(1000)
    window.setWindowTitle("TIMER GREENSCREEN")
    window.show()

    # DonationDisplay Window
    donation_window = DonationDisplay(font_name=constants.FONT_NAME)
    donation_window.resize(800, 300)
    donation_window.setWindowTitle("DONATION GREENSCREEN")
    donation_window.show()

    # ElapsedTimer Window
    elapsed_time_window = ElapsedTimer(initial_time=TOTAL_TIME_ADDED, font_name=constants.FONT_NAME, font_size=constants.FONT_SIZE, bg_color=constants.BG_COLOR)
    elapsed_time_window.setWindowTitle("MINUTE COUNTER GREENSCREEN")
    elapsed_time_window.show()

    sys.exit(app.exec_())
