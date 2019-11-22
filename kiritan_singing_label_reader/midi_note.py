from pathlib import Path
from typing import Union

import midi


class Note:
    def __init__(self, pitch: int, start: float, end: float):
        self.pitch = pitch
        self.start = start
        self.end = end

    def __repr__(self):
        return f'Note(pitch=\'{self.pitch}\', start={self.start}, end={self.end})'


class MidiNoteReader():
    def __init__(self, path: Union[str, Path]):
        self.song = midi.read_midifile(str(path))

    def get_bpm(self):
        bpm = None
        for track in self.song:
            for event in track:
                if isinstance(event, midi.SetTempoEvent):
                    new_bpm = event.get_bpm()
                    assert bpm is None or bpm == new_bpm
                    bpm = new_bpm
        return bpm

    def get_resolution(self):
        return self.song.resolution

    def get_notes(self):
        self.song.make_ticks_abs()
        bpm = self.get_bpm()
        resolution = self.get_resolution()

        def _tick_to_second(tick: float):
            return tick * 60 / bpm / resolution

        notes = []
        start_states = {}
        for track in self.song:
            for event in track:
                if isinstance(event, midi.NoteOnEvent):
                    pitch = event.get_pitch()

                    if pitch in start_states:  # note off
                        pitch = event.get_pitch()
                        note = Note(
                            pitch=pitch,
                            start=start_states.pop(pitch),
                            end=_tick_to_second(event.tick),
                        )
                        notes.append(note)

                    if event.get_velocity() > 0:  # note on
                        assert pitch not in start_states
                        start_states[pitch] = _tick_to_second(event.tick)

        return notes
