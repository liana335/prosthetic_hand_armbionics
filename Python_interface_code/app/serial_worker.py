import serial
from PySide6.QtCore import Signal, Slot, QObject

PACKET_SIZE = 8


class SerialWorker(QObject):
    data_received = Signal(object, object)
    raw_data_received = Signal(object)

    error = Signal(str)
    finished = Signal()

    def __init__(self, port, baud):
        super().__init__()

        self.port = port
        self.baud = baud

        self.serial = None
        self.running = False

    @Slot()
    def run(self):
        try:
            self.serial = serial.Serial(self.port, self.baud)
            self.running = True

            while self.running:
                data = self.serial.read(PACKET_SIZE)

                if not self.running:
                    break

                if len(data) != PACKET_SIZE:
                    continue

                self.raw_data_received.emit(data)

                emg1_filtered = data[0] | data[1] << 8 | data[2] << 16 | data[3] << 24
                emg2_filtered = data[4] | data[5] << 8 | data[6] << 16 | data[7] << 24

                self.data_received.emit(emg1_filtered, emg2_filtered)

        except Exception as error:
            self.error.emit(str(error))

        finally:
            self.running = False

            if self.serial is not None:
                self.serial.close()
                self.serial = None

            self.finished.emit()

    @Slot()
    def stop(self):
        self.running = False