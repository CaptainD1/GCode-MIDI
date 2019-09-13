import serial
import time
from gcode_midi_2 import notes_from_file 
from printer import Printer
'''
def send_song(printer, gcode):
    time.sleep(5)
    print("Resetting position...")
    printer.write(b'G90\nG1 Y80\n')
    print("Reset complete")
    time.sleep(5)
    print(printer2.read(printer2.inWaiting()).decode())
    time.sleep(5)
    print("Starting!")
    for line in gcode:
        printer.write(line.encode())
        response = printer.readline()
        print(line.strip())
        print(response.decode(), end='')
        while response[:2] != b'ok':
            response = printer.readline()
            print(response.decode(), end='')'''

def execute_gcode(gcode1, gcode2):

    ready1 = True
    ready2 = True
    i1 = 0
    i2 = 0

    while len(gcode1) > 0 and len(gcode2) > 0:

        if ready1:
            code1 = gcode1.pop(0).encode()
            print('send 1:',code1)
            printer1.write(code1)
            ready1 = False
            i1 += 1

        if ready2:
            code2 = gcode2.pop(0).encode()
            print('send 2:',code2)
            printer2.write(code2)
            ready2 = False
            i2 += 1

        if printer1.inWaiting() and len(gcode1) > 0:
            response1 = printer1.readline()
            if response1[:2] == b'ok':
                ready1 = True
            print('recv 1:', response1)

        if printer2.inWaiting() and len(gcode2) > 0:
            response2 = printer2.readline()
            if response2[:2] == b'ok':
                ready2 = True
            print('recv 2:', response2)

        print(i1, i2, '    ', end='\r')

FILENAME = '../Dark_World_Theme.mid'

serial_ports = ['/dev/ttyACM' + str(i) for i in range(2)]

printers = [Printer(port) for port in serial_ports]

all_tracks = notes_from_file(FILENAME)

tracks = [tracks[0], tracks[2]]

for printer in printers:
    printer.init()

startup_commands = ['G26', 'G21', 'G90', 'G28']

for command in startup_commands:
    ready = all([printer.ready() for printer in printers])
    while not ready:
        time.sleep(0.001)

    for printer in printers:
        printer.send(command)

print("Starting program...")

'''execute_gcode(gcode1[:6], gcode2[:6])
time.sleep(3)

if printer1.inWaiting():
    print(1,printer1.read(printer1.inWaiting()))
if printer2.inWaiting():
    print(2,printer2.read(printer2.inWaiting()))

time.sleep(1)
execute_gcode(gcode1[3:], gcode2[3:])

while True:
    printer2.write((input('>>> ') + '\n').encode())'''
