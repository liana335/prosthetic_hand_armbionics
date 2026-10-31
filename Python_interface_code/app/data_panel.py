from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QComboBox
)


HORIZONTAL_SPACING = 5
VERTICAL_SPACING = 5
SPACING = 20

COMBO_HEIGHT = 30

EMG1_CHANNEL = 1
EMG2_CHANNEL = 2


class DataPanel(QFrame):
    def __init__(self, user):
        super().__init__()

        self.user = user
        self.session = None

        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()

        layout.setContentsMargins(SPACING, SPACING, SPACING, SPACING)
        layout.setHorizontalSpacing(HORIZONTAL_SPACING)
        layout.setVerticalSpacing(VERTICAL_SPACING)

        # Column titles
        row_0_title = QLabel("")
        row_0_title.setObjectName("rowTitle")

        emg1_title = QLabel("EMG 1")
        emg2_title = QLabel("EMG 2")

        emg1_title.setObjectName("columnTitle")
        emg2_title.setObjectName("columnTitle")

        layout.addWidget(row_0_title, 0, 0)
        layout.addWidget(emg1_title, 0, 1)
        layout.addWidget(emg2_title, 0, 2)

        # Idle voltages
        row_1_title = QLabel("Idle voltage")
        row_1_title.setObjectName("rowTitle")

        self.emg1_idle_voltage = QLabel()
        self.emg2_idle_voltage = QLabel()

        layout.addWidget(row_1_title, 1, 0)
        layout.addWidget(self.emg1_idle_voltage, 1, 1)
        layout.addWidget(self.emg2_idle_voltage, 1, 2)

        self.add_separator(layout, 2)

        # Active voltages
        row_3_title = QLabel("Active voltage")
        row_3_title.setObjectName("rowTitle")

        self.emg1_active_voltage = QLabel()
        self.emg2_active_voltage = QLabel()

        layout.addWidget(row_3_title, 3, 0)
        layout.addWidget(self.emg1_active_voltage, 3, 1)
        layout.addWidget(self.emg2_active_voltage, 3, 2)

        self.add_separator(layout, 4)

        # Sample selectors
        row_5_title = QLabel("Sample")
        row_5_title.setObjectName("rowTitle")

        self.emg1_sample_selector = QComboBox()
        self.emg2_sample_selector = QComboBox()

        self.emg1_sample_selector.setFixedHeight(COMBO_HEIGHT)
        self.emg2_sample_selector.setFixedHeight(COMBO_HEIGHT)

        layout.addWidget(row_5_title, 5, 0)
        layout.addWidget(self.emg1_sample_selector, 5, 1)
        layout.addWidget(self.emg2_sample_selector, 5, 2)

        # Timestamps
        row_6_title = QLabel("Timestamp")
        row_6_title.setObjectName("rowTitle")

        self.emg1_timestamp = QLabel()
        self.emg2_timestamp = QLabel()

        layout.addWidget(row_6_title, 6, 0)
        layout.addWidget(self.emg1_timestamp, 6, 1)
        layout.addWidget(self.emg2_timestamp, 6, 2)

        self.add_separator(layout, 7)

        # Sample voltages
        row_8_title = QLabel("Sample voltage")
        row_8_title.setObjectName("rowTitle")

        self.emg1_sample_voltage = QLabel()
        self.emg2_sample_voltage = QLabel()

        layout.addWidget(row_8_title, 8, 0)
        layout.addWidget(self.emg1_sample_voltage, 8, 1)
        layout.addWidget(self.emg2_sample_voltage, 8, 2)

        self.add_separator(layout, 9)

        # Durations
        row_10_title = QLabel("Duration")
        row_10_title.setObjectName("rowTitle")

        self.emg1_duration = QLabel()
        self.emg2_duration = QLabel()

        layout.addWidget(row_10_title, 10, 0)
        layout.addWidget(self.emg1_duration, 10, 1)
        layout.addWidget(self.emg2_duration, 10, 2)

        # Connections
        self.emg1_sample_selector.currentIndexChanged.connect(self.update_emg1_sample)
        self.emg2_sample_selector.currentIndexChanged.connect(self.update_emg2_sample)

        self.setLayout(layout)
        self.update_data()

    def add_separator(self, layout, row):
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)

        layout.addWidget(separator, row, 0, 1, 3)

    def update_user(self, user):
        self.user = user
        self.session = None

        self.update_data()

    def update_session(self, session):
        self.session = session

        self.update_session_voltages()
        self.update_sample_selectors()

    def update_data(self):
        if self.session is not None:
            self.update_session_voltages()
            self.update_sample_info()
        else:
            self.update_voltage_values()
            self.clear_sample_selectors()

    def update_voltage_values(self):
        # Idle voltages
        self.set_voltage_label(self.emg1_idle_voltage, self.user.emg1_idle_voltage)
        self.set_voltage_label(self.emg2_idle_voltage, self.user.emg2_idle_voltage)

        # Active voltages
        self.set_voltage_label(self.emg1_active_voltage, self.user.emg1_active_voltage)
        self.set_voltage_label(self.emg2_active_voltage, self.user.emg2_active_voltage)

    def set_voltage_label(self, label, value):
        if value is None:
            label.clear()
            return

        label.setText(f"{value:.0f} mV")

    def update_session_voltages(self):
        if self.session is None:
            self.emg1_idle_voltage.clear()
            self.emg2_idle_voltage.clear()
            self.emg1_active_voltage.clear()
            self.emg2_active_voltage.clear()
            return

        emg1_idle = self.session.emg1_idle_history
        emg2_idle = self.session.emg2_idle_history
        emg1_samples = self.session.emg1_samples
        emg2_samples = self.session.emg2_samples

        emg1_idle_mean = (sum(emg1_idle) / len(emg1_idle) if emg1_idle else 0)
        emg2_idle_mean = (sum(emg2_idle) / len(emg2_idle) if emg2_idle else 0)

        emg1_active_mean = (sum(sample.sample_voltage for sample in emg1_samples) / len(emg1_samples) if emg1_samples else 0)
        emg2_active_mean = (sum(sample.sample_voltage for sample in emg2_samples) / len(emg2_samples) if emg2_samples else 0)

        self.set_voltage_label(self.emg1_idle_voltage, emg1_idle_mean)
        self.set_voltage_label(self.emg2_idle_voltage, emg2_idle_mean)
        self.set_voltage_label(self.emg1_active_voltage, emg1_active_mean)
        self.set_voltage_label(self.emg2_active_voltage, emg2_active_mean)

    def update_sample_selectors(self):
        self.emg1_sample_selector.blockSignals(True)
        self.emg2_sample_selector.blockSignals(True)

        self.emg1_sample_selector.clear()
        self.emg2_sample_selector.clear()

        if self.session is not None:
            for i in range(len(self.session.emg1_samples)):
                self.emg1_sample_selector.addItem(f"sample {i + 1}")

            for i in range(len(self.session.emg2_samples)):
                self.emg2_sample_selector.addItem(f"sample {i + 1}")

        self.emg1_sample_selector.blockSignals(False)
        self.emg2_sample_selector.blockSignals(False)

        if self.session is None:
            self.clear_sample_info(EMG1_CHANNEL)
            self.clear_sample_info(EMG2_CHANNEL)
            return

        if self.session.emg1_samples:
            self.emg1_sample_selector.setCurrentIndex(len(self.session.emg1_samples) - 1)
        else:
            self.clear_sample_info(EMG1_CHANNEL)

        if self.session.emg2_samples:
            self.emg2_sample_selector.setCurrentIndex(len(self.session.emg2_samples) - 1)
        else:
            self.clear_sample_info(EMG2_CHANNEL)

        self.update_emg1_sample(self.emg1_sample_selector.currentIndex())
        self.update_emg2_sample(self.emg2_sample_selector.currentIndex())

    def update_sample_info(self):
        if self.session is None:
            return

        emg1_count = len(self.session.emg1_samples)
        emg2_count = len(self.session.emg2_samples)

        while self.emg1_sample_selector.count() < emg1_count:
            index = self.emg1_sample_selector.count()
            self.emg1_sample_selector.addItem(f"sample {index + 1}")

        while self.emg2_sample_selector.count() < emg2_count:
            index = self.emg2_sample_selector.count()
            self.emg2_sample_selector.addItem(f"sample {index + 1}")

        if emg1_count > 0:
            self.emg1_sample_selector.setCurrentIndex(emg1_count - 1)
        else:
            self.clear_sample_info(EMG1_CHANNEL)

        if emg2_count > 0:
            self.emg2_sample_selector.setCurrentIndex(emg2_count - 1)
        else:
            self.clear_sample_info(EMG2_CHANNEL)

    def update_emg1_sample(self, index):
        if self.session is None or not self.session.emg1_samples:
            self.clear_sample_info(EMG1_CHANNEL)
            return

        if index < 0 or index >= len(self.session.emg1_samples):
            return

        sample = self.session.emg1_samples[index]

        self.emg1_timestamp.setText(sample.timestamp.strftime("%H:%M:%S"))
        self.emg1_sample_voltage.setText(f"{sample.sample_voltage:.0f} mV")
        self.emg1_duration.setText(self.format_duration(sample.duration))

    def update_emg2_sample(self, index):
        if self.session is None or not self.session.emg2_samples:
            self.clear_sample_info(EMG2_CHANNEL)
            return

        if index < 0 or index >= len(self.session.emg2_samples):
            return

        sample = self.session.emg2_samples[index]

        self.emg2_timestamp.setText(sample.timestamp.strftime("%H:%M:%S"))
        self.emg2_sample_voltage.setText(f"{sample.sample_voltage:.0f} mV")
        self.emg2_duration.setText(self.format_duration(sample.duration))

    def clear_sample_info(self, channel):
        if channel == EMG1_CHANNEL:
            self.emg1_timestamp.clear()
            self.emg1_sample_voltage.clear()
            self.emg1_duration.clear()

        elif channel == EMG2_CHANNEL:
            self.emg2_timestamp.clear()
            self.emg2_sample_voltage.clear()
            self.emg2_duration.clear()

    def clear_sample_selectors(self):
        self.emg1_sample_selector.blockSignals(True)
        self.emg2_sample_selector.blockSignals(True)

        self.emg1_sample_selector.clear()
        self.emg2_sample_selector.clear()

        self.emg1_sample_selector.blockSignals(False)
        self.emg2_sample_selector.blockSignals(False)

        self.clear_sample_info(EMG1_CHANNEL)
        self.clear_sample_info(EMG2_CHANNEL)

    def format_duration(self, duration):
        total_seconds = int(duration.total_seconds())

        minutes = total_seconds // 60
        seconds = total_seconds % 60

        return f"{minutes:02d}:{seconds:02d}"