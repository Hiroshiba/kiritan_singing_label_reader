import argparse
from operator import attrgetter
from pathlib import Path

from kiritan_singing_label_reader import MidiNoteReader


def sample_pitch_range(
        kiritan_singing_directory: Path,
):
    midi_paths = (kiritan_singing_directory / 'midi_label/').glob('*.mid')
    pitches = []
    for path in midi_paths:
        notes = MidiNoteReader(path).get_notes()
        pitches += list(map(attrgetter('pitch'), notes))

    print('min', min(pitches))  # min 53
    print('max', max(pitches))  # max 76


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kiritan_singing_directory', type=Path)
    sample_pitch_range(**vars(parser.parse_args()))
