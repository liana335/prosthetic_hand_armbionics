class RunningAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.count = 0
        self.mean = 0

    def update(self, value):
        if self.count < self.window_size:
            self.count += 1
            self.mean = (value + self.mean * (self.count - 1)) / self.count

        else:
            self.mean = (value + self.mean * (self.window_size - 1)) / self.window_size

        return self.mean