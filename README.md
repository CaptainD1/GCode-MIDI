# GCode-MIDI
This is a Python3 program that converts MIDI files into G-Code that can be run on 3D printers to play music.

At the moment, this only works with a single track without any chords, but I'm planning on adding up to 3 parts at once, each played by a different axis on a printer.

I have only tested this out on a Lulzbot Mini printer, but theoretically this should work on any 3D printer that makes noise when moving.
You will just need to change the `Y_MIN`, `Y_MAX`, and maybe other constants to work with your printer.

## Requirements
This requires Mido to run. It can be installed by running the following command:

`pip install mido`
