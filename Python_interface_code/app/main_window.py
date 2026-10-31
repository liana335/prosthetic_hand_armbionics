from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QThread
import os
from datetime import datetime
from app.serial_worker import SerialWorker
from app.realtime_plot import RealtimePlot
from app.history_plot import HistoryPlotter
from app.user_panel import UserPanel
from app.data_panel import DataPanel
from core.event_detector import EventDetector
from user.user_info import User
from user.history_save_load import save_user


WINDOW_TITLE = "Armbionics"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900

SPACING = 20

BUTTON_HEIGHT = 40
TERMINAL_WINDOW_HEIGHT = 70
TERMINAL_LINES = 3

PLOT_WINDOW_SIZE = 200
HISTORY_INTERVAL = 5
IDLE_HISTORY_INTERVAL = 5_000

PORT = "COM3"
# PORT = "COM7"
BAUD = 115200

THRESHOLD = 1500
WINDOW_SIZE = 10

EMG1_CHANNEL = 1
EMG2_CHANNEL = 2

DATA_FOLDER = "data"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.user = User(id="000", name="Anonymous", surname="", prosthesis_type="")

        self.reset_anonymous_user()

        self.emg1_detector = EventDetector(threshold=THRESHOLD, window_size=WINDOW_SIZE)
        self.emg2_detector = EventDetector(threshold=THRESHOLD, window_size=WINDOW_SIZE)

        self.serial_thread = None
        self.serial_worker = None

        self.idle_history_timer = QTimer()
        self.idle_history_timer.setInterval(IDLE_HISTORY_INTERVAL)
        self.idle_history_timer.timeout.connect(self.save_idle_history)

        self.emg1_current_idle_voltage = 0
        self.emg2_current_idle_voltage = 0

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)
        main_layout.setSpacing(SPACING)

        # Left panel
        left_panel = QWidget()

        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(SPACING)

        # User panel
        self.user_panel = UserPanel(self.user)
        self.user_panel.setObjectName("panel")

        self.user_panel.emg_pause_requested.connect(self.pause_emg)
        self.user_panel.user_changed.connect(self.change_user)

        # Data
        self.data_panel = DataPanel(self.user)
        self.data_panel.setObjectName("panel")

        left_panel_layout.addWidget(self.user_panel, 1)
        left_panel_layout.addWidget(self.data_panel, 4)

        # Right panel
        right_panel = QWidget()

        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(SPACING)
        
        # Terminal
        terminal_panel = QWidget()
        terminal_panel.setObjectName("panel")

        terminal_panel_layout = QVBoxLayout(terminal_panel)
        terminal_panel_layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)

        terminal_title = QLabel("Serial terminal")
        terminal_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        terminal_title.setObjectName("plotTitle")

        self.emg_terminal = QPlainTextEdit()
        self.emg_terminal.setReadOnly(True)
        self.emg_terminal.setFixedHeight(TERMINAL_WINDOW_HEIGHT)
        self.emg_terminal.setObjectName("emgTerminal")

        terminal_panel_layout.addWidget(terminal_title)
        terminal_panel_layout.addWidget(self.emg_terminal)

        # Realtime plotter
        realtime_plot_panel = QWidget()
        realtime_plot_panel.setObjectName("panel")

        realtime_plot_panel_layout = QVBoxLayout(realtime_plot_panel)
        realtime_plot_panel_layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)

        realtime_plot_title = QLabel("EMG Filtered signal")
        realtime_plot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        realtime_plot_title.setObjectName("plotTitle")

        self.realtime_plot = RealtimePlot(window=PLOT_WINDOW_SIZE)

        realtime_plot_panel_layout.addWidget(realtime_plot_title)
        realtime_plot_panel_layout.addWidget(self.realtime_plot)

        # History plotter
        history_plot_panel = QWidget()
        history_plot_panel.setObjectName("panel")

        history_plot_panel_layout = QVBoxLayout(history_plot_panel)
        history_plot_panel_layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)

        history_plot_title = QLabel("EMG History")
        history_plot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        history_plot_title.setObjectName("plotTitle")

        self.history_plot = HistoryPlotter(intervals=HISTORY_INTERVAL)
        self.history_plot.session_selected.connect(self.data_panel.update_session)

        #Buttons
        start_button = QPushButton("Start/Continue")
        pause_button = QPushButton("Pause")
        reset_button = QPushButton("Reset")
        show_history_button = QPushButton("Show history")

        for button in (start_button, pause_button, reset_button, show_history_button):
            button.setFixedHeight(BUTTON_HEIGHT)
            button.setObjectName("button")

        start_button.clicked.connect(self.start_emg)
        pause_button.clicked.connect(self.pause_emg)
        reset_button.clicked.connect(self.reset_emg)
        show_history_button.clicked.connect(self.show_history)

        button_layout = QHBoxLayout()

        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addWidget(pause_button)
        button_layout.addWidget(reset_button)
        button_layout.addWidget(show_history_button)
        button_layout.addStretch()

        history_plot_panel_layout.addWidget(history_plot_title)
        history_plot_panel_layout.addWidget(self.history_plot)
        history_plot_panel_layout.addLayout(button_layout)

        right_panel_layout.addWidget(terminal_panel)
        right_panel_layout.addWidget(realtime_plot_panel)
        right_panel_layout.addWidget(history_plot_panel)

        right_panel_layout.addStretch()

        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)

    def get_user_filename(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        return os.path.join(DATA_FOLDER, f"user{self.user.id}.json")

    def save_current_user(self):
        filename = self.get_user_filename()

        save_user(self.user, filename)

    def reset_anonymous_user(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        anonymous_user = User(id="000", name="Anonymous", surname="", prosthesis_type="")
        filename = os.path.join(DATA_FOLDER, "user000.json")

        save_user(anonymous_user, filename)

    def start_serial(self):
        self.serial_thread = QThread()

        self.serial_worker = SerialWorker(PORT, BAUD)

        self.serial_worker.moveToThread(self.serial_thread)

        self.serial_thread.started.connect(self.serial_worker.run)

        self.serial_worker.data_received.connect(self.update_realtime_plot)
        self.serial_worker.raw_data_received.connect(self.update_terminal)
        self.serial_worker.error.connect(self.handle_serial_error)
        self.serial_worker.finished.connect(self.serial_thread.quit)
        self.serial_worker.finished.connect(self.serial_worker.deleteLater)

        self.serial_thread.start()

    def start_emg(self):
        if self.user.current_session is None:
            self.emg1_detector.reset()
            self.emg2_detector.reset()
    
            self.emg1_current_idle_voltage = 0
            self.emg2_current_idle_voltage = 0
    
            self.user.start_session()
            self.data_panel.update_session(self.user.current_session)
    
        if self.serial_thread is None or not self.serial_thread.isRunning():
            self.start_serial()
    
        self.idle_history_timer.start()
        self.realtime_plot.plot()

    def pause_emg(self):
        self.idle_history_timer.stop()

        if self.serial_worker is not None:
            self.serial_worker.stop()

        self.realtime_plot.pause()

        if self.user.current_session is not None:
            self.save_idle_history()
            self.user.end_session()
            self.save_current_user()

        self.history_plot.update_sessions(self.user)

    def reset_emg(self):
        if self.user.current_session is not None:
            session_index = self.user.sessions.index(self.user.current_session)
        else:
            session_index = self.history_plot.get_current_session_index()

        if session_index < 0:
            return

        reply = QMessageBox.question(
            self,
            "Reset session",
            "Are you sure you want to reset the selected session?\n\n"
            "All data from this session will be permanently deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.idle_history_timer.stop()

        if self.serial_worker is not None:
            self.serial_worker.stop()

        self.realtime_plot.pause()

        self.user.reset_session(session_index)

        self.emg1_detector.reset()
        self.emg2_detector.reset()

        self.emg1_current_idle_voltage = 0
        self.emg2_current_idle_voltage = 0

        self.save_current_user()

        self.realtime_plot.reset()
        self.history_plot.update_sessions(self.user)
        self.data_panel.update_user(self.user)

    def update_terminal(self, data):
        byte_string = "".join(f"{byte:02X} " for byte in data)
        line = f"RX | {len(data):02d} | {byte_string}"

        self.emg_terminal.appendPlainText(line)

        document = self.emg_terminal.document()

        while document.blockCount() > TERMINAL_LINES:
            cursor = self.emg_terminal.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

        scrollbar = self.emg_terminal.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_history(self):
        self.pause_emg()

    def save_idle_history(self):
        if self.user.current_session is None:
            return

        if self.emg1_current_idle_voltage > 0:
            self.user.add_idle_voltage(channel=EMG1_CHANNEL, voltage=self.emg1_current_idle_voltage)

        if self.emg2_current_idle_voltage > 0:
            self.user.add_idle_voltage(channel=EMG2_CHANNEL, voltage=self.emg2_current_idle_voltage)

    def update_realtime_plot(self, emg1_filtered, emg2_filtered):
        timestamp = datetime.now()

        self.realtime_plot.update(emg1_filtered, emg2_filtered)

        # EMG 1
        emg1_sample, emg1_idle_voltage = self.emg1_detector.update(timestamp=timestamp, voltage=emg1_filtered)

        if emg1_idle_voltage is not None:
            self.emg1_current_idle_voltage = emg1_idle_voltage

        if emg1_sample is not None:
            self.user.add_sample(channel=EMG1_CHANNEL, sample=emg1_sample)

        # EMG 2
        emg2_sample, emg2_idle_voltage = self.emg2_detector.update(timestamp=timestamp, voltage=emg2_filtered)

        if emg2_idle_voltage is not None:
            self.emg2_current_idle_voltage = emg2_idle_voltage

        if emg2_sample is not None:
            self.user.add_sample(channel=EMG2_CHANNEL, sample=emg2_sample)

        self.data_panel.update_data()

    def handle_serial_error(self, message):
        print("Serial error: ", message)

    def change_user(self, user):
        if self.user.current_session is not None:
            self.pause_emg()

        elif self.serial_worker is not None:
            self.serial_worker.stop()

        self.user = user

        self.data_panel.update_user(user)

        self.emg1_detector.reset()
        self.emg2_detector.reset()

        self.emg1_current_idle_voltage = 0
        self.emg2_current_idle_voltage = 0

        self.realtime_plot.reset()
        self.history_plot.update_sessions(user)

        self.emg_terminal.clear()

    def closeEvent(self, event):
        self.idle_history_timer.stop()

        if self.serial_worker is not None:
            self.serial_worker.stop()

        if self.serial_thread is not None and self.serial_thread.isRunning():
            self.serial_thread.quit()
            self.serial_thread.wait()

        if self.user.current_session is not None:
            self.save_idle_history()
            self.user.end_session()

            self.save_current_user()

        event.accept()