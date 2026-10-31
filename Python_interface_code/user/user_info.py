from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class Sample:
    timestamp: datetime
    sample_voltage: float
    duration: timedelta

@dataclass
class Session:
    session_start: datetime
    session_end: datetime | None = None

    emg1_idle_history: list[float] = field(default_factory=list)
    emg2_idle_history: list[float] = field(default_factory=list)

    emg1_samples: list[Sample] = field(default_factory=list)
    emg2_samples: list[Sample] = field(default_factory=list)

class User:
    def __init__(self, id="000", name="Anonymous", surname="", prosthesis_type=""):
        self.id = id
        self.name = name
        self.surname = surname
        self.prosthesis_type = prosthesis_type

        self.emg1_idle_voltage = 0
        self.emg2_idle_voltage = 0

        self.emg1_active_voltage = 0
        self.emg2_active_voltage = 0

        self.sessions = []

        self.current_session = None

    def start_session(self):
        if self.current_session is not None:
            return

        session = Session(session_start=datetime.now())

        self.sessions.append(session)
        self.current_session = session

    def end_session(self):
        if self.current_session is None:
            return
        
        self.current_session.session_end = datetime.now()
        self.current_session = None

        self.calculate_voltages()

    def reset_session(self, index):
        if index < 0 or index >= len(self.sessions):
            return

        if self.current_session is self.sessions[index]:
            self.current_session = None

        self.sessions.pop(index)

        self.calculate_voltages()

    def add_sample(self, channel, sample):
        if self.current_session is None:
            return
        
        if channel == 1:
            self.current_session.emg1_samples.append(sample)

        elif channel == 2:
            self.current_session.emg2_samples.append(sample)

        self.calculate_active_voltages()

    def add_idle_voltage(self, channel, voltage):
        if self.current_session is None:
            return

        if channel == 1:
            self.current_session.emg1_idle_history.append(voltage)

        elif channel == 2:
            self.current_session.emg2_idle_history.append(voltage)

        self.calculate_idle_voltages()

    def calculate_active_voltages(self):
        emg1_sample_voltages = []
        emg2_sample_voltages = []

        for session in self.sessions:
            for sample in session.emg1_samples:
                emg1_sample_voltages.append(sample.sample_voltage)

            for sample in session.emg2_samples:
                emg2_sample_voltages.append(sample.sample_voltage)

        if emg1_sample_voltages:
            self.emg1_active_voltage = sum(emg1_sample_voltages) / len(emg1_sample_voltages)
        else:
            self.emg1_active_voltage = 0

        if emg2_sample_voltages:
            self.emg2_active_voltage = sum(emg2_sample_voltages) / len(emg2_sample_voltages)
        else:
            self.emg2_active_voltage = 0

    def calculate_idle_voltages(self):
        emg1_idle_voltages = []
        emg2_idle_voltages = []

        for session in self.sessions:
            for voltage in session.emg1_idle_history:
                emg1_idle_voltages.append(voltage)

            for voltage in session.emg2_idle_history:
                emg2_idle_voltages.append(voltage)

        if emg1_idle_voltages:
            self.emg1_idle_voltage = sum(emg1_idle_voltages) / len(emg1_idle_voltages)
        else:
            self.emg1_idle_voltage = 0

        if emg2_idle_voltages:
            self.emg2_idle_voltage = sum(emg2_idle_voltages) / len(emg2_idle_voltages)
        else:
            self.emg2_idle_voltage = 0

    def calculate_voltages(self):
        self.calculate_active_voltages()
        self.calculate_idle_voltages()

    @property
    def emg1_samples(self):
        if self.current_session is not None:
            return self.current_session.emg1_samples

        if self.sessions:
            return self.sessions[-1].emg1_samples

        return []

    @property
    def emg2_samples(self):
        if self.current_session is not None:
            return self.current_session.emg2_samples

        if self.sessions:
            return self.sessions[-1].emg2_samples

        return []

    @property
    def emg1_idle_history(self):
        if self.current_session is not None:
            return self.current_session.emg1_idle_history

        if self.sessions:
            return self.sessions[-1].emg1_idle_history

        return []

    @property
    def emg2_idle_history(self):
        if self.current_session is not None:
            return self.current_session.emg2_idle_history

        if self.sessions:
            return self.sessions[-1].emg2_idle_history
        
        return []