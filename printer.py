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

        if not self._ready:
        while self._ser.inWaiting():
            line = self.readline()
            if line[:2] == b'ok':
                self._ready = True:
                break
        
        if self._ready:
            self._ser.write((command + '\n' if command[-1] != '\n' else '').encode())
            self._ready = False
            return True
        return False

    def ready(self):

        return self._ready
