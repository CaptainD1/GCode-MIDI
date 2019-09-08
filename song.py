class Note:

    def __init__(self, note, time, length):

        self.note = note
        self.time = time
        self.length = length

    def __str__(self):
        return "note: {}, time: {}, length: {}".format(self.note, self.time, self.length)

    def __repr__(self):
        return str(self)

class Song:

    def __init__(self):

        self.notes = {}
        self.abstime = 0