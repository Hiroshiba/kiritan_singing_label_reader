import argparse
from itertools import chain, groupby
from operator import attrgetter
from pathlib import Path
from typing import Sequence, List

import numpy

from kiritan_singing_label_reader import Phoneme, MidiNoteReader


class JapaneseTableCell:
    def __init__(self, line: str):
        words = line.split()
        if len(words) == 2:
            self.hiragana = words[0]
            self.vowel = words[1]
            self.coonsonant = None
        elif len(words) == 3:
            self.hiragana = words[0]
            self.vowel = words[2]
            self.coonsonant = words[1]
        else:
            raise ValueError(line)


def get_durations(label_paths: Sequence[Path]):
    phonemes = chain.from_iterable(
        Phoneme.load_julius_list(label_path)
        for label_path in label_paths
    )

    key = attrgetter('name')
    phonemes = {
        k: list(v)
        for k, v in groupby(sorted(phonemes, key=key), key=key)
    }

    durations = {
        k: numpy.mean([p.end - p.start for p in v])
        for k, v in phonemes.items()
    }

    return durations


def sample_auto_phoneme_labeling(
        kiritan_singing_directory: Path,
        lyric_path: Path,
        midi_path: Path,
        output_path: Path,
):
    label_paths = sorted((kiritan_singing_directory / 'mono_label/').glob('*.lab'))
    durations = get_durations(label_paths)

    japanese_table = (kiritan_singing_directory / 'japanese.table').read_text().splitlines()
    cells = map(JapaneseTableCell, japanese_table)
    cells = {c.hiragana: c for c in cells}

    lyrics = lyric_path.read_text().split()
    notes = MidiNoteReader(midi_path).get_notes()
    assert len(lyrics) == len(notes)

    # phoneme labeling
    phonemes: List[Phoneme] = []
    phonemes.append(Phoneme(name='pau', start=0, end=notes[0].start))
    for lyric, note in zip(lyrics, notes):
        cell = cells[lyric]

        # coonsonant
        if cell.coonsonant is not None:
            p = Phoneme(name=cell.coonsonant, start=note.start - durations[cell.coonsonant], end=note.start)

            # replace
            if len(phonemes) > 0 and phonemes[-1].end > p.start:
                phonemes[-1].end = p.start

            phonemes.append(p)

        # vowel
        p = Phoneme(name=cell.vowel, start=note.start, end=note.end)
        phonemes.append(p)

    # fill brink phoneme
    for pre_phoneme, post_phoneme in zip(phonemes[:-1], phonemes[1:]):
        if pre_phoneme.end < post_phoneme.start:
            p = Phoneme(name='br', start=pre_phoneme.end, end=post_phoneme.start)
            phonemes.append(p)

    # add pause phoneme at start and end
    phonemes.append(Phoneme(name='pau', start=notes[-1].end, end=notes[-1].end + 1))

    # sort
    phonemes = sorted(phonemes, key=attrgetter('start'))

    # save
    Phoneme.write_julius_list(output_path, phonemes=phonemes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kiritan_singing_directory', type=Path)
    parser.add_argument('--lyric_path', type=Path)
    parser.add_argument('--midi_path', type=Path)
    parser.add_argument('--output_path', type=Path)
    sample_auto_phoneme_labeling(**vars(parser.parse_args()))
