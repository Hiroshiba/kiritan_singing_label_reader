from pathlib import Path
from typing import Union, Sequence

import numpy

from kiritan_singing_label_reader.midi_note import Note


class Phoneme:
    phoneme_names = (
        'pau', 'br', 'a', 'b', 'ch', 'cl', 'd', 'e', 'f', 'g', 'gy', 'h', 'hy', 'i', 'j', 'k', 'ky', 'm', 'my', 'n',
        'N', 'ny', 'o', 'p', 'py', 'r', 'ry', 's', 'sh', 't', 'ts', 'u', 'v', 'w', 'y', 'z',
    )

    def __init__(
            self,
            name: str,
            start: float = None,
            end: float = None,
    ) -> None:
        self.name = name
        self.start = start
        self.end = end

    def __eq__(self, other: 'Phoneme'):
        return self.name == other.name

    def __repr__(self):
        return f'Phoneme(phoneme=\'{self.name}\', start={self.start}, end={self.end})'

    def verify(self):
        assert self.name in self.phoneme_names, f'{self.name} is not defined.'

    @property
    def duration(self):
        return self.end - self.start

    @classmethod
    def parse(cls, s: str):
        words = s.split()
        return cls(
            start=float(words[0]),
            end=float(words[1]),
            name=words[2],
        )

    @classmethod
    def load_julius_list(cls, path: Union[str, Path]):
        phonemes = [
            cls.parse(s)
            for s in Path(path).read_text().splitlines()
            if len(s) > 0
        ]
        for phoneme in phonemes:
            phoneme.verify()
        return phonemes

    @classmethod
    def write_julius_list(cls, path: Union[str, Path], phonemes: Sequence['Phoneme']):
        s = ''
        for phoneme in phonemes:
            s += f'{phoneme.start} {phoneme.end} {phoneme.name}\n'

        Path(path).write_text(s)


def filter_phoneme_with_note(phonemes: Sequence[Phoneme], notes: Sequence[Note]):
    """filter un pairwise phoneme label"""
    pau_phoneme = Phoneme('pau')
    assert phonemes[0] == pau_phoneme and phonemes[-1] == pau_phoneme

    pau_indexes = numpy.where(numpy.array(phonemes) == pau_phoneme)[0]

    filtered_phonemes = []
    for i, j in zip(pau_indexes[:-1], pau_indexes[1:]):
        start = phonemes[i + 1].start - 1
        end = phonemes[j - 1].end + 1
        num_note = len(list(filter(lambda note: start < note.start and note.end < end, notes)))

        if num_note > 0:
            filtered_phonemes += phonemes[i:j]

    filtered_phonemes += [phonemes[-1]]
    return filtered_phonemes


def verify_phoneme_and_note(phonemes: Sequence[Phoneme], notes: Sequence[Note]):
    pau_phoneme = Phoneme('pau')
    br_phoneme = Phoneme('br')

    def _is_near(phoneme: Phoneme, note: Note):
        return \
            (phoneme.start - 1 < note.start and note.end < phoneme.end + 1) \
            or \
            (note.start - 1 < phoneme.start and phoneme.end < note.end + 1)

    # eliminate 'pau' and 'br'
    phonemes = list(filter(lambda phoneme: phoneme != pau_phoneme and phoneme != br_phoneme, phonemes))

    matrix = numpy.empty((len(phonemes), len(notes)), dtype=bool)
    for i, phoneme in enumerate(phonemes):
        for j, note in enumerate(notes):
            matrix[i, j] = _is_near(phoneme, note)

    return matrix.any(axis=0).all() and matrix.any(axis=1).all()
