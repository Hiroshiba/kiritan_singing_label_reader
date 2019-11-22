import argparse
from pathlib import Path

from kiritan_singing_label_reader import MidiNoteReader, Phoneme, filter_phoneme_with_note, verify_phoneme_and_note


def sample(
        kiritan_singing_directory: Path,
):
    midi_paths = sorted((kiritan_singing_directory / 'midi_label/').glob('*.mid'))
    label_paths = sorted((kiritan_singing_directory / 'mono_label/').glob('*.lab'))

    for i, (midi_path, label_path) in enumerate(zip(midi_paths, label_paths)):
        # get midi notes
        midi_reader = MidiNoteReader(midi_path)
        notes = midi_reader.get_notes()

        # get phonemes
        phonemes = Phoneme.load_julius_list(label_path)

        # '06' and '08' have un pairwise phoneme label
        # ref. https://github.com/mmorise/kiritan_singing
        if i in [5, 7]:
            phonemes = filter_phoneme_with_note(phonemes, notes)
            Phoneme.write_julius_list(f'{i + 1:0>2}.lab', phonemes)

        ok = verify_phoneme_and_note(phonemes, notes)
        print(midi_path)
        print(label_path)
        print(ok)

        break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kiritan_singing_directory', type=Path)
    sample(**vars(parser.parse_args()))
