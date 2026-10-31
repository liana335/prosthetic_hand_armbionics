import random
from PySide6.QtCore import QObject, QTimer, Signal


class EMGGenerator(QObject):
    data_received = Signal(float, float)
    error = Signal(str)

    SAMPLE_INTERVAL = 50

    IDLE_VOLTAGE = 1000
    ACTIVE_MIN = 2200
    ACTIVE_MAX = 2800

    def __init__(self):
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_sample)

        self.emg1_active = False
        self.emg2_active = False

        self.emg1_value = self.IDLE_VOLTAGE
        self.emg2_value = self.IDLE_VOLTAGE

        self.emg1_remaining = 0
        self.emg2_remaining = 0

    def start(self):
        if not self.timer.isActive():
            self.timer.start(self.SAMPLE_INTERVAL)

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

    def generate_sample(self):
        self.update_emg1()
        self.update_emg2()

        self.data_received.emit(self.emg1_value, self.emg2_value)

    def update_emg1(self):
        if self.emg1_remaining <= 0:
            self.emg1_active = random.random() < 0.03

            if self.emg1_active:
                self.emg1_remaining = random.randint(20, 40)

        else:
            self.emg1_remaining -= 1

        if self.emg1_active:
            target = random.uniform(self.ACTIVE_MIN, self.ACTIVE_MAX)
        else:
            target = self.IDLE_VOLTAGE

        self.emg1_value += (target - self.emg1_value) * 0.15

        self.emg1_value += random.gauss(0, 30)

    def update_emg2(self):
        if self.emg2_remaining <= 0:
            self.emg2_active = random.random() < 0.03

            if self.emg2_active:
                self.emg2_remaining = random.randint(20, 40)

        else:
            self.emg2_remaining -= 1

        if self.emg2_active:
            target = random.uniform(self.ACTIVE_MIN, self.ACTIVE_MAX)
        else:
            target = self.IDLE_VOLTAGE

        self.emg2_value += (target - self.emg2_value) * 0.15

        self.emg2_value += random.gauss(0, 30)