import mido

FILENAME = "D:\\Users\\legoh\\Music\\midi\\Don't-Stop-Me-Now.mid"

def notes_from_file(filename):

    mid = mido.MidiFile(FILENAME)
    tpb = mid.ticks_per_beat
    tps = 8000*tpb

    notes = {}
    current_notes = {}

    for track in mid.tracks:
        for note in track:
            if hasattr(note, 'channel') and note.channel not in notes:
                notes[note.channel] = []

    for track in mid.tracks:
        abstime = 0

        for note in track:
            abstime += note.time
            if note.type == 'note_on' and note.velocity != 0:
                current_notes[note.channel] = note.time
            elif note.type =='note_off' or (note.type == 'note_on' and note.velocity == 0):
                notes[note.channel].append((note.note, current_notes[note.channel]/tps, note.time/tps))
            elif note.type == 'set_tempo':
                tps = 1000000/note.tempo*tpb

    return notes