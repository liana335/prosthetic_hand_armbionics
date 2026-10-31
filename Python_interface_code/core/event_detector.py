from user.user_info import Sample
from filters.running_average import RunningAverage

class EventDetector:
    def __init__(self, threshold, window_size=10):
        self.threshold = threshold
        self.active = False

        self.idle_calculate = RunningAverage(window_size)

        self.event_start_time = None
        self.event_sum = 0
        self.event_count = 0

    def update(self, timestamp, voltage):
        if voltage < self.threshold:
            idle_voltage = self.idle_calculate.update(voltage)

            if self.active:
                self.active = False

                if self.event_count > 0:    
                    sample_voltage = self.event_sum / self.event_count
                    duration = timestamp - self.event_start_time

                    sample = Sample(timestamp=self.event_start_time, sample_voltage=sample_voltage, duration=duration)

                else:
                    sample = None

                self.event_start_time = None
                self.event_sum = 0
                self.event_count = 0

                return sample, idle_voltage
            
            return None, idle_voltage
        
        
        if not self.active:
            self.active = True
            self.event_start_time = timestamp
            self.event_sum = 0
            self.event_count = 0

        self.event_sum += voltage
        self.event_count += 1

        return None, None

    def reset(self):
        self.active = False

        self.idle_calculate = RunningAverage(self.idle_calculate.window_size)

        self.event_start_time = None
        self.event_sum = 0
        self.event_count = 0
