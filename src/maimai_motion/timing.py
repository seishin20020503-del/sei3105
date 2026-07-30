"""Match detected touch events against chart notes and compute timing deviation.

Matching is greedy nearest-time-first per note, which is a simplification:
in very dense passages it can occasionally assign a touch to a less-ideal
note. This is acceptable given the tight matching window used in practice.
"""
from dataclasses import dataclass

from .chart import Note
from .touch_detection import TouchEvent


@dataclass
class TimingMatch:
    note: Note
    touch: TouchEvent

    @property
    def delta_sec(self) -> float:
        """Positive: touched late (after the note). Negative: touched early."""
        return self.touch.time_sec - self.note.time_sec


def match_notes_to_touches(
    notes: list[Note],
    touches: list[TouchEvent],
    max_window_sec: float = 0.5,
) -> list[TimingMatch]:
    matches = []
    used = [False] * len(touches)
    for note in notes:
        best_idx = None
        best_delta = None
        for i, touch in enumerate(touches):
            if used[i]:
                continue
            delta = abs(touch.time_sec - note.time_sec)
            if delta <= max_window_sec and (best_delta is None or delta < best_delta):
                best_delta = delta
                best_idx = i
        if best_idx is not None:
            used[best_idx] = True
            matches.append(TimingMatch(note=note, touch=touches[best_idx]))
    matches.sort(key=lambda m: m.note.time_sec)
    return matches
