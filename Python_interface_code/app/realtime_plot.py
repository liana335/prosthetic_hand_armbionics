from collections import deque
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout
)


FIGSIZE = (10, 5)
DEFAULT_PLOT_WINDOW_SIZE = 200

EMG1_LABEL = "Emg 1 filtered"
EMG2_LABEL = "Emg 2 filtered"

EMG1_COLOR = "#184e77"
EMG2_COLOR = "#b5e48c"

X_LABEL = "Samples"
Y_LABEL = "Voltage (mV)"

Y_LIM = 5000

LABEL_SIZE = 10
LABEL_COLOR = "white"

LEGEND_FONT_SIZE = 8

FACECOLOR = "white"


class RealtimePlot(QWidget):
    def __init__(self, window=DEFAULT_PLOT_WINDOW_SIZE, parent=None):
        super().__init__(parent)

        self.window = window

        self.paused = True

        self.emg1_filtered = deque([0] * window, maxlen=window)
        self.emg2_filtered = deque([0] * window, maxlen=window)

        self.x = range(window)

        self.figure = Figure(figsize=FIGSIZE, constrained_layout=True)
        self.figure.patch.set_alpha(0)

        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.set_facecolor(FACECOLOR)

        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        
        self.setup_plot()

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def setup_plot(self):
        self.ax.set_xlim(0, self.window - 1)
        self.ax.set_ylim(0, Y_LIM)

        self.ax.set_xlabel(X_LABEL, fontsize=LABEL_SIZE, color=LABEL_COLOR)
        self.ax.set_ylabel(Y_LABEL, fontsize=LABEL_SIZE, color=LABEL_COLOR)

        self.emg1_filtered_line, = self.ax.plot(self.x, self.emg1_filtered, label=EMG1_LABEL, color=EMG1_COLOR)
        self.emg2_filtered_line, = self.ax.plot(self.x, self.emg2_filtered, label=EMG2_LABEL, color=EMG2_COLOR)

        self.ax.tick_params(axis="both",colors=LABEL_COLOR)
        self.ax.grid(True)
        self.ax.legend(loc="upper right", fontsize=LEGEND_FONT_SIZE)

        self.canvas.draw()

    def update(self, emg1_filtered, emg2_filtered):
        if self.paused:
            return

        self.emg1_filtered.append(emg1_filtered)
        self.emg2_filtered.append(emg2_filtered)

        self.emg1_filtered_line.set_ydata(self.emg1_filtered)
        self.emg2_filtered_line.set_ydata(self.emg2_filtered)

        self.canvas.draw_idle()

    def plot(self):
        self.paused = False

    def pause(self):
        self.paused = True

    def reset(self):
        self.emg1_filtered = deque([0] * self.window, maxlen=self.window)
        self.emg2_filtered = deque([0] * self.window, maxlen=self.window)

        self.emg1_filtered_line.set_ydata(self.emg1_filtered)
        self.emg2_filtered_line.set_ydata(self.emg2_filtered)

        self.canvas.draw_idle()   
