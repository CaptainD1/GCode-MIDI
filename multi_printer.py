import serial
import time
from note_converter import *
from printer import Printer

FILENAME = '../Dark_World_Theme.mid'

serial_ports = ['/dev/ttyACM' + str(i) for i in range(2)]
printers = [Printer(port) for port in serial_ports]
all_tracks = notes_from_file(FILENAME)
tracks = [all_tracks[0], all_tracks[2]]

for printer in printers:
    printer.init()

startup_commands = ['G21', 'G90', 'G28']

for command in startup_commands:
    while not all([printer.ready() for printer in printers]):
        time.sleep(0.001)

    for printer in printers:
        printer.send(command)

    print(command)

print("Starting program...")

track_range = range(len(tracks))

note_index = [0 for i in track_range]
positions = [START for i in track_range]
start_time = time.time()

while any([note_index[i] < len(tracks[i]) for i in track_range]):
    current_time = time.time()
    for i in track_range:
        if tracks[i][note_index[i]].time + start_time >= current_time:
            gcode, pos = convert_note(tracks[i][note_index[i]], positions[i])
            printers[i].send(gcode)