## kiritan_singing_label_reader
The reader for [東北きりたん歌唱データベース](https://github.com/mmorise/kiritan_singing)'s label data in python.
You can read midi notes and phoneme labels with using this library.

### Requirements
Python 3.6

### Usage
```bash
pip install git+https://github.com/Hiroshiba/kiritan_singing_label_reader
```

### Example
```python
# get midi notes
from kiritan_singing_label_reader import MidiNoteReader

midi_reader = MidiNoteReader('/path/to/midi_label/01.mid')
notes = midi_reader.get_notes()
"""
[
    Note(pitch='64', start=18.947376, end=19.350747871874997),
    Note(pitch='71', start=19.342112999999998, end=21.904202840624997),
    Note(pitch='68', start=22.105272, end=22.30181813125),
    ...
]
"""
from kiritan_singing_label_reader import Phoneme

phonemes = Phoneme.load_julius_list('/path/to/mono_label/01.lab')
"""
[
    Phoneme(phoneme='pau', start=0.0, end=18.6263777),
    Phoneme(phoneme='br', start=18.6263777, end=19.0916217),
    Phoneme(phoneme='k', start=19.0916217, end=19.1636238),
    ...
]
"""

# you can filter un pairwise phoneme label
from kiritan_singing_label_reader import filter_phoneme_with_note
phonemes = filter_phoneme_with_note(phonemes, notes)
```

There are more samples in [sample.py](sample.py)

### License
[MIT LICENSE](LICENSE)
