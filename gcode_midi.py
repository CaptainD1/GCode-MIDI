import mido

# MIDI takes a number from 0 to 127 to represent the notes for the following frequencies
notes = [8.18, 8.66, 9.18, 9.72, 10.30, 10.91, 11.56, 12.25, 12.98, 13.75, 14.57, 15.43, 16.35,
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

# Declare constants
TIME_MOD = 200000 # This will need to be adjusted better later
VELOCITY_MULT_Y = 10 # Adjusting this should essentially 'tune' the 3D printer
MIN_Y = 0
MAX_Y = 160

# Starting value for Y position
current_y = (MIN_Y + MAX_Y) / 2

# Starting value for GCODE
instructions = "G26\nG21\nG90\nG1 Y" + str(current_y) + " F6000\nG4 P1000\n"
last_minutes = 0

def main():

    # TODO: Get this to work with command line arguments.
    path = input("Enter path to MIDI file: ")
    output = input("Enter path for GCode file (it should end with .gcode): ")
    
    channel = None
    while channel == None:
        try:
            response = input("Enter channel to use (default: 0): ")
            # If nothing is entered, set channel to zero
            if response == '':
                channel = 0
            else:
                channel = int(response)
                # Go to except block if channel is negative
                if channel < 0:
                    raise ValueError

        # Is run when channel is not an integer or negative
        except ValueError:
            print("Error: Must enter a non-negative integer value")
            # Reset channel to None so the loop continues
            channel = None

    try:
        from_file(path, output)
    except FileNotFoundError:
        print("Error: File not found")

def from_file(infile, outfile, channel=0):
    '''Convert a MIDI file into a GCODE file'''
    mid = mido.MidiFile(infile)
    for note in mid.tracks[channel]:
        # Everything other than 'note_on' type will just be unnecesary information
        if note.type == 'note_on':
            convertNote(note)

    write_gcode(outfile)

def convertNote(note):
    '''Converts a note object from mido into a GCODE command.
    At the moment, this only uses the Y axis of the 3D printer and can only play one track at a time.
    
    I know, this should probably just be a class instead of using global variables.
    This program used to work a lot differently. I'll fix this later.

    I need to make a new music representation class or something for better conversion later as well.
    Currently, this is very rough and will be extremely hard to get working with more than 1 track.
    It will also probably break a bit if any track has any chords.
    '''

    global instructions
    global last_minutes
    global current_y

    # In the MIDI files I was testing out, if note velocity is 0, then that's the part that stops the note.
    # The time component for them shows how long after the note started was.
    if note.velocity == 0:

        # List contains all Y positions the printer should go to.
        new_ys = []

        # Determine distance from velocity (mm/min: note frequency) and time (minutes: note length) to find distance (mm)
        velocity = notes[note.note] * VELOCITY_MULT_Y
        minutes = note.time/TIME_MOD
        distance = velocity * minutes

        last_minutes = minutes

        # Try to go towards max Y. If it doesn't fit, go towards min Y. If neither fit, go back and forth as much as required.
        while distance > 0:
            if current_y + distance <= MAX_Y:
                print("Forward", current_y, distance)
                current_y += distance
                new_ys.append(current_y)
                distance = 0
            elif current_y - distance >= MIN_Y:
                print("Backward", current_y, distance)
                current_y -= distance
                new_ys.append(current_y)
                distance = 0
            elif current_y + distance - MAX_Y < distance - current_y + MIN_Y:
                print("Hit Forward", current_y, distance)
                new_ys.append(MAX_Y)
                distance -= MAX_Y - current_y
                current_y = MAX_Y
            else:
                print("Hit Backward", current_y, distance)
                new_ys.append(MIN_Y)
                distance -= current_y - MIN_Y
                current_y = MIN_Y

        for new_y in new_ys:
            instructions += "G1 Y" + str(int(new_y)) + " F" + str(int(velocity)) + "\n"
            #instructions += "G4 P10\n"

    else:
        # Add a short delay between notes to differentiate them or add rests
        # last_minutes is required because the G4 (wait) command starts counting before the
        #   3D printer movement is done
        instructions += "G4 P" + str(int((last_minutes + note.time/TIME_MOD) * 60000)) + "\n"
        last_minutes = 0

def write_gcode(filename):
    '''Write all commands to a file and clear.

    I KNOW, DON'T USE GLOBAL VARIABLES FOR THIS REASON. I'LL FIX IT LATER.'''

    global instructions
    global current_y

    # Reset Y starting position
    current_y = int((MIN_Y + MAX_Y) / 2)

    # Open and write instructions to file, while adding reset instructions
    file = open(filename, "w")
    file.write(instructions + "G4 P1000\nG1 Y" + str(current_y) + " F6000\n")

    # Reset instructions for next time
    instructions = "G26\nG21\nG90\nG1 Y" + str(current_y) + " F6000\nG4 P1000\n"
    
    file.close()


main()