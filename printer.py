import serial
import time

class Printer:

    def __init__(self, port, baudrate = 250000):

        self._ser = serial.Serial(port, baudrate)

        self._ready = False
        self._starttime = time.time()

    def init(self):

        delay = 1.5 + self._starttime - time.time()
        if delay > 0:
            time.sleep(delay)

        self._ready = True

        return self.read()

    def read(self):

        return self._ser.read(self._ser.inWaiting()).decode()

    def readline(self):

        return self._ser.readline().decode()

    def send(self, command):
        
        if self.ready():
            self._ser.write((command + '\n' if command[-1] != '\n' else '').encode())
            self._ready = False
            return True
        return False

    def ready(self):

        if not self._ready:
            while self._ser.inWaiting():
                message = self._ser.read(self._ser.inWaiting())
                if message[:2] == b'ok' or b'\nok' in message:
                    self._ready = True
                    break

        print(self._ready)
        return self._ready
