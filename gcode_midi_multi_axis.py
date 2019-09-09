import mido
import os
import math
from song import Note

FILENAME = "D:\\Users\\legoh\\Music\\midi\\Sea_Shanty2.mid"
OUTPUT_FOLDER = "D:\\Users\\legoh\\Documents\\3D\\3D Printing\\"
OUTPUT_NAME = 'SeaShanty2-'

# MIDI takes a number from 0 to 127 to represent the notes for the following frequencies
NOTES = [8.18, 8.66, 9.18, 9.72, 10.30, 10.91, 11.56, 12.25, 12.98, 13.75, 14.57, 15.43, 16.35,
        17.32, 18.35, 19.45, 20.60, 21.83, 23.12, 24.50, 25.96, 27.50, 29.14, 30.87, 32.70,
        34.65, 36.71, 38.89, 41.20, 43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 61.74, 65.41,
        69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00, 103.83, 110.00, 116.54, 123.47,
        130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08,
        246.94, 261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00,
        466.16, 493.88, 523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61,
        880.00, 932.33, 987.77, 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98,
        1567.98, 1661.22, 1760.00, 1864.66, 1975.53, 2093.00, 2217.46, 2349.32, 2489.02,
        2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3729.31, 3951.07, 4186.01,
        4434.92, 4698.64, 4978.03, 5274.04, 5587.65, 5919.91, 6271.93, 6644.88, 7040.00,
        7458.62, 7902.13, 8372.02, 8869.84, 9397.27, 9956.06, 10548.08, 11175.30, 11839.82,
        12543.85, 13289.75]

# The speed offset of the printer. Adjusting this will 'tune' the printer
VELOCITY_MULT = (10, 10, .1)
MIN = (0, 0, 0)
MAX = (160, 160, 160)
START = [(MIN[i] + MAX[i])//2 for i in range(len(MIN))]
START_INSTRUCTIONS = "G26\nG21\nG90\nG1 X" + str(START[0]) + \
    " Y" + str(START[1]) + " Z" + str(START[2]) + " F6000\nG4 P1000\n"
END_INSTRUCTIONS = "\nG4 P1000\nG1 X" + str(START[0]) + \
    " Y" + str(START[1]) + " Z" + str(START[2]) + " F6000\n"

def main():

    notes = notes_from_file(FILENAME)
    for channel in notes:
        print(channel, len(notes[channel]))

    full_export(notes, OUTPUT_FOLDER, OUTPUT_NAME)

def notes_from_file(filename):

    mid = mido.MidiFile(FILENAME)
    tpb = mid.ticks_per_beat
    tps = 8000*tpb

    notes = {}
    start_times = {}

    for track in mid.tracks:
        for note in track:
            if hasattr(note, 'channel') and note.channel not in notes:
                notes[note.channel] = []

    for track in mid.tracks:
        abstime = 0

        for note in track:
            abstime += note.time / tps
            if note.type == 'note_on' and note.velocity != 0:
                start_times[note.channel] = abstime
            elif note.type =='note_off' or (note.type == 'note_on' and note.velocity == 0):
                notes[note.channel].append(Note(note.note, int(start_times[note.channel]*1000), int((abstime - start_times[note.channel])*1000)))
            elif note.type == 'set_tempo':
                tps = 1000000/note.tempo*tpb

    return notes

def convert_notes(notes):

    gcode = ''
    #pos = START[1]

    pos = START.copy()

    axis_range = range(len(notes))
    indexes = [0 for i in axis_range]
    available_notes = []
    current_notes = []
    unused_notes = []
    velocities = []
    distance = []
    current_time = 0

    while any([indexes[i] < len(notes[i]) for i in axis_range]):
        # Only use notes from tracks with remaining notes        
        for i in axis_range:
            if indexes[i] < len(notes[i]):
                available_notes.append(notes[i][indexes[i]])

        # Find all notes with the lowest start time
        current_notes.append(available_notes[0])
        if len(available_notes) > 1:
            for note in available_notes[1:]:
                if note.time < current_notes[0].time:
                    current_notes.clear()
                    current_notes.append(note)
                elif note.time == current_notes[0].time:
                    current_notes.append(note)

        # Increment indexes for all notes being used and populate unused notes list
        for i in axis_range:
            if notes[i][indexes[i]] in current_notes:
                indexes[i] += 1
            else:
                unused_notes.append(notes[i][indexes[i]])
        
        # Find start and end times
        start = current_notes[0].time
        end = min([note.time + note.length for note in current_notes] + [note.time for note in unused_notes])
        duration = end - start

        # Do any delays
        delay = start - current_time
        if delay != 0:
            gcode += "G4 P{}\n".format(delay)

        # Calculate motion in each dimension
        for note in current_notes:
            velocities.append(NOTES[note.note] * VELOCITY_MULT[0]) # TODO: This needs to know which axis use
            # TODO: Potentially have every list the same size, but have None in all unused parts
            # TODO: Or just have a list of indexes for used notes and unused notes
            distance.append(int(velocities[-1] * duration / 60000)) # Notes are in ms

        # Calculate overall velocity
        velocity = int(math.sqrt(sum([vel**2 for vel in velocities])))

        for i in range(len(current_notes)):
            if pos[i] + distance[i] <= MAX[0]:
                pos[i] += distance[i]
            else:
                pos[i] -= distance[i]

        # Modify Gcode
        gcode += "G1 X{} Y{} Z{} F{}\n".format(pos[1], pos[0], pos[2], velocity)

        # Clean up
        current_time = end
        available_notes.clear()
        current_notes.clear()
        unused_notes.clear()
        velocities.clear()
        distance.clear()
            

    '''for note in notes:

        velocity = NOTES[note.note] * VELOCITY_MULT[axis]
        distance = velocity * note[2] / 60 # notes are in seconds

        # Try to go towards max Y. If it doesn't fit, go towards min Y. If neither fit, go back and forth as much as required.
        while distance > 0:
            if pos + distance <= MAX[1]:
                pos += distance
                new_positions.append(pos)
                distance = 0
            elif pos - distance >= MIN[1]:
                pos -= distance
                new_positions.append(pos)
                distance = 0
            elif pos + distance - MAX[1] < distance - pos + MIN[1]:
                new_positions.append(MAX[1])
                distance -= MAX[1] - pos
                pos = MAX[1]
            else:
                new_positions.append(MIN[1])
                distance -= pos - MIN[1]
                pos = MIN[1]

        gcode += "G4 P" + str(int(note[1] * 1000)) + '\n'
        for new_pos in new_positions:
            gcode += "G1 Y" + str(int(new_pos)) + " F" + str(int(velocity)) + "\n"
        new_positions.clear()
        
        # BREAK

        pos = [i for i in START]
        new_positions = [[] for i in START]

        while distance > 0:
            if pos[axis] + distance <= MAX[axis]:
                pos[axis] += distance
                new_positions[axis].append(pos[axis])
                distance = 0
            elif pos[axis] - distance >= MIN[axis]:
                pos[axis] -= distance
                new_positions[axis].append(pos[axis])
                distance = 0
            elif pos[axis] + distance - MAX[axis] < distance - pos[axis] + MIN[axis]:
                new_positions[axis].append(MAX[axis])
                distance -= MAX[axis] - pos[axis]
                pos[axis] = MAX[axis]
            else:
                new_positions[axis].append(MIN[axis])
                distance -= pos[axis] - MIN[axis]
                pos[axis] = MIN[axis]'''

    return gcode
            
def full_export(notes, folder, filename):
    for track in notes:
        export_gcode(os.path.join(folder, filename + str(track) + '.gcode'), convert_notes([notes[track],]))

def export_gcode(filename, gcode):

    with open(filename, 'w') as file:
        file.write(START_INSTRUCTIONS + gcode + END_INSTRUCTIONS)

main()