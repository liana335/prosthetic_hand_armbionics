from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QFrame
)
from PySide6.QtCore import Qt, Signal


FIGSIZE = (10, 5)
DEFAULT_INTERVALS = 5

HORIZONTAL_SPACING = 10
VERTICAL_SPACING = 5

BAR_WIDTH = 0.1
BAR_SPACING = 0.05

X_LABEL = "Time"
Y_LABEL = "Voltage (mV)"

Y_LIM = 5000

LABEL_SIZE = 10
LABEL_COLOR = "white"

VALUE_LABEL_SIZE = 8

LEGEND_FONT_SIZE = 8

FACECOLOR = "white"

EMG1_ACTIVE_LABEL = "EMG 1 Active voltage"
EMG1_IDLE_LABEL = "EMG 1 Idle voltage"
EMG2_ACTIVE_LABEL = "EMG 2 Active voltage"
EMG2_IDLE_LABEL = "EMG 2 Idle voltage"

EMG1_ACTIVE_COLOR = "#184e77"
EMG1_IDLE_COLOR = "#1a759f"
EMG2_ACTIVE_COLOR = "#b5e48c"
EMG2_IDLE_COLOR = "#d9ed92"

ROW_1_LABEL = "EMG 1 events"
ROW_2_LABEL = "EMG 2 events"

COMBO_HEIGHT = 30

LAYOUT_SPACING = 20




class HistoryPlotter(QWidget):
    session_selected = Signal(object)
    
    def __init__(self, intervals=DEFAULT_INTERVALS, parent=None):
        super().__init__(parent)

        self.intervals = intervals

        self.session_selector = QComboBox()
        self.session_selector.setFixedHeight(COMBO_HEIGHT)
        self.session_selector.currentIndexChanged.connect(self.select_session)

        self.sessions = []

        self.figure = Figure(figsize=FIGSIZE, constrained_layout=True)
        self.figure.patch.set_alpha(0)

        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background: transparent;")

        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.set_facecolor(FACECOLOR)

        self.event_count_layout = QGridLayout()
        self.event_count_layout.setContentsMargins(0, 0, 0, 0)

        self.event_count_layout.setHorizontalSpacing(HORIZONTAL_SPACING)
        self.event_count_layout.setVerticalSpacing(VERTICAL_SPACING)

        emg1_event_title = QLabel(ROW_1_LABEL)
        emg2_event_title = QLabel(ROW_2_LABEL)

        emg1_event_title.setObjectName("eventsCountLabel")
        emg2_event_title.setObjectName("eventsCountLabel")

        self.add_separator(self.event_count_layout, 0)

        self.event_count_layout.addWidget(emg1_event_title, 1, 0)
        self.event_count_layout.addWidget(emg2_event_title, 2, 0)

        self.emg1_event_labels = []
        self.emg2_event_labels = []

        for i in range(self.intervals):
            emg1_label = QLabel("0")
            emg2_label = QLabel("0")

            emg1_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            emg2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.emg1_event_labels.append(emg1_label)
            self.emg2_event_labels.append(emg2_label)

            self.event_count_layout.addWidget(emg1_label, 1, i + 1)
            self.event_count_layout.addWidget(emg2_label, 2, i + 1)

        self.add_separator(self.event_count_layout, 3)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(LAYOUT_SPACING)

        layout.addWidget(self.session_selector)
        layout.addWidget(self.canvas)
        layout.addLayout(self.event_count_layout)

        self.setup_plot()

    def add_separator(self, layout, row):
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)

        layout.addWidget(separator, row, 0, 1, self.intervals + 1)

    def setup_plot(self):
        self.ax.clear()
        self.ax.set_facecolor(FACECOLOR)

        self.setup_axes()

        self.ax.set_xlim(0, 1)
        self.ax.set_xticks([0, 1])
        self.ax.set_xticklabels(["Session start", "Session end"], color=LABEL_COLOR)

        self.canvas.draw()

    def setup_axes(self):
        self.ax.set_xlabel(X_LABEL, fontsize=LABEL_SIZE, color=LABEL_COLOR)
        self.ax.set_ylabel(Y_LABEL, fontsize=LABEL_SIZE, color=LABEL_COLOR)

        self.ax.set_ylim(0, Y_LIM)

        self.ax.tick_params(axis="both", colors=LABEL_COLOR)

        for spine in self.ax.spines.values():
            spine.set_color(LABEL_COLOR)

        self.ax.grid(True, axis="y", alpha=0.3)

    def update_sessions(self, user):
        self.sessions = user.sessions

        self.session_selector.blockSignals(True)
        self.session_selector.clear()

        for i, session in enumerate(self.sessions):
            start = session.session_start.strftime("%d-%m-%Y %H:%M:%S")

            if session.session_end is not None:
                end = session.session_end.strftime("%d-%m-%Y %H:%M:%S")
                text = f"Session {i + 1} ({start} - {end})"
            else:
                text = f"Session {i + 1} ({start})"

            self.session_selector.addItem(text)

        if self.sessions:
            last_index = len(self.sessions) - 1
            self.session_selector.setCurrentIndex(last_index)
        else:
            last_index = -1

        self.session_selector.blockSignals(False)

        if last_index >= 0:
            self.select_session(last_index)
        else:
            self.setup_plot()
            self.clear_event_counts()

    def select_session(self, index):
        if index < 0 or index >= len(self.sessions):
            return

        session = self.sessions[index]

        self.update_history(session)
        self.session_selected.emit(session)

    def update_history(self, session):
        self.ax.clear()

        if session.session_start is None or session.session_end is None:
            self.setup_plot()
            return

        session_duration = session.session_end - session.session_start

        if session_duration.total_seconds() <= 0:
            self.setup_plot()
            return

        interval_duration = session_duration / self.intervals

        emg1_active_values = [[] for _ in range(self.intervals)]
        emg2_active_values = [[] for _ in range(self.intervals)]

        emg1_event_counts = [0] * self.intervals
        emg2_event_counts = [0] * self.intervals

        for sample in session.emg1_samples:
            time_till_event = sample.timestamp - session.session_start

            interval = int(time_till_event.total_seconds() / interval_duration.total_seconds())

            if interval >= self.intervals:
                interval = self.intervals - 1

            if interval < 0:
                continue

            emg1_active_values[interval].append(sample.sample_voltage)
            emg1_event_counts[interval] += 1
       
        for sample in session.emg2_samples:
            time_till_event = sample.timestamp - session.session_start

            interval = int(time_till_event.total_seconds() / interval_duration.total_seconds())

            if interval >= self.intervals:
                interval = self.intervals - 1

            if interval < 0:
                continue

            emg2_active_values[interval].append(sample.sample_voltage)
            emg2_event_counts[interval] += 1

        emg1_active_means = [(sum(values) / len(values) if values else 0) for values in emg1_active_values]
        emg2_active_means = [(sum(values) / len(values) if values else 0) for values in emg2_active_values]

        emg1_idle_values = self.calculate_idle_history(session.emg1_idle_history)
        emg2_idle_values = self.calculate_idle_history(session.emg2_idle_history)

        x = list(range(self.intervals))

        emg1_active_x = [value - BAR_WIDTH * 3 / 2 - 2* BAR_SPACING for value in x]
        emg1_idle_x = [value - BAR_WIDTH / 2 - BAR_SPACING for value in x]
        emg2_active_x = [value + BAR_WIDTH / 2 + BAR_SPACING for value in x]
        emg2_idle_x = [value + BAR_WIDTH * 3 / 2 + 2 * BAR_SPACING for value in x]

        self.ax.bar(emg1_active_x, emg1_active_means, width=BAR_WIDTH, label=EMG1_ACTIVE_LABEL, color=EMG1_ACTIVE_COLOR)
        self.ax.bar(emg1_idle_x, emg1_idle_values, width=BAR_WIDTH, label=EMG1_IDLE_LABEL, color=EMG1_IDLE_COLOR)
        
        self.ax.bar(emg2_active_x, emg2_active_means, width=BAR_WIDTH, label=EMG2_ACTIVE_LABEL, color=EMG2_ACTIVE_COLOR)
        self.ax.bar(emg2_idle_x, emg2_idle_values, width=BAR_WIDTH, label=EMG2_IDLE_LABEL, color=EMG2_IDLE_COLOR)

        self.setup_axes()

        self.ax.set_xlim(-0.5, self.intervals - 0.5)

        for x in range(self.intervals - 1):
            self.ax.axvline(x + 0.5, color="gray", alpha=0.35, linewidth=1, zorder=1)

        self.ax.set_xlabel(X_LABEL, fontsize=LABEL_SIZE, color=LABEL_COLOR, labelpad=30)

        start_text = session.session_start.strftime("%d-%m-%Y\n%H:%M:%S")
        end_text = session.session_end.strftime("%d-%m-%Y\n%H:%M:%S")

        self.ax.set_xticks([])
        self.ax.text(0, -0.4, start_text, transform=self.ax.transAxes, ha="center", va="top", color=LABEL_COLOR)
        self.ax.text(1, -0.4, end_text, transform=self.ax.transAxes, ha="center", va="top", color=LABEL_COLOR)
        
        self.ax.legend(loc="upper right", fontsize=LEGEND_FONT_SIZE)

        for i in range(self.intervals):
            self.emg1_event_labels[i].setText(str(emg1_event_counts[i]))
            self.emg2_event_labels[i].setText(str(emg2_event_counts[i]))

        self.add_bar_value_labels(emg1_active_x, emg1_active_means)
        self.add_bar_value_labels(emg1_idle_x, emg1_idle_values)
        self.add_bar_value_labels(emg2_active_x, emg2_active_means)
        self.add_bar_value_labels(emg2_idle_x, emg2_idle_values)

        self.canvas.draw()

    def add_bar_value_labels(self, x_values, values):
        for x, value in zip(x_values, values):
            if value <= 0:
                continue

            self.ax.text(x, -0.08, f"{value:.0f}", transform=self.ax.get_xaxis_transform(), ha="center", va="top", rotation=90, fontsize=VALUE_LABEL_SIZE, color=LABEL_COLOR)

    def calculate_idle_history(self, values):
        if not values:
            return [0] * self.intervals

        total_values = len(values)

        idle_means = []

        for i in range(self.intervals):
            start = i * total_values // self.intervals
            end = (i + 1) * total_values // self.intervals

            interval_values = values[start:end]

            if interval_values:
                idle_mean = sum(interval_values) / len(interval_values)
            else:
                idle_mean = 0

            idle_means.append(idle_mean)

        return idle_means

    def get_current_session_index(self):
        return self.session_selector.currentIndex()

    def clear_event_counts(self):
        for label in self.emg1_event_labels:
            label.setText("0")

        for label in self.emg2_event_labels:
            label.setText("0")

    def clear(self):
        self.setup_plot()
        self.clear_event_counts()