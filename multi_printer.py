import serial
import time
import os
from note_converter import *
from printer import Printer

directory = '../midi/'

files = os.listdir(directory)

print("Available songs:")
for i in range(len(files)):
    print(' ', i, files[i])
file_index = int(input("Enter index of file: "))

FILENAME = os.path.join(directory, files[file_index])

all_tracks = notes_from_file(FILENAME)

print('\nAvailable tracks:')
for channel in all_tracks:
    print(' ', channel, len(all_tracks[channel]))

track_nums = input("Enter tracks to use separated by spaces: ").split()
track_nums = [int(num) for num in track_nums]

tracks = [all_tracks[i] for i in track_nums]

serial_ports = ['/dev/ttyACM' + str(i) for i in range(len(tracks))]
printers = [Printer(port) for port in serial_ports]

for printer in printers:
    printer.init()

startup_commands = ['G21', 'G90', 'G28', 'G1 Y{}'.format(START)]

for command in startup_commands:
    while not all([printer.ready() for printer in printers]):
        time.sleep(0.001)

    for printer in printers:
        printer.send(command)

    print(command)


track_range = range(len(tracks))

note_index = [0 for i in track_range]
positions = [START for i in track_range]

time.sleep(5)

start_time = time.time()

print("Starting program...")

while any([note_index[i] < len(tracks[i]) for i in track_range]):
    current_time = time.time()
    for i in track_range:
        if note_index[i] < len(tracks[i]) and tracks[i][note_index[i]].time / 1000 + start_time <= current_time:
            gcode, pos = convert_note(tracks[i][note_index[i]], positions[i])
            positions[i] = pos
            print(i, repr(gcode), tracks[i][note_index[i]].time / 1000, tracks[i][note_index[i]].length / 1000)
            printers[i].send(gcode.strip())
            note_index[i] += 1
