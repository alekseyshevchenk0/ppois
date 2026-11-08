from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List

from .constants import (
    DEFAULT_VOLUME,
    EQ_BANDS,
    EQ_MAX_GAIN,
    EQ_MIN_GAIN,
    HISTORY_LIMIT,
    MAX_VOLUME,
    MIN_VOLUME,
    SKIP_RATIO,
)
from .exceptions import EmptyQueueError, InvalidTrackDataError, InvalidVolumeError
from .media import Track


@dataclass(eq=False)
class EqualizerPreset:
    name: str
    gains: List[int] = field(default_factory=lambda: [0] * EQ_BANDS)

    def validate(self) -> None:
        if len(self.gains) != EQ_BANDS:
            raise InvalidTrackDataError("Неверное число полос эквалайзера")
        if any(not EQ_MIN_GAIN <= gain <= EQ_MAX_GAIN for gain in self.gains):
            raise InvalidTrackDataError("Усиление вне диапазона")


@dataclass(eq=False)
class Equalizer:
    gains: List[int] = field(default_factory=lambda: [0] * EQ_BANDS)
    enabled: bool = True

    def apply_gains(self, gains: List[int]) -> None:
        EqualizerPreset("custom", gains).validate()
        self.gains = list(gains)

    def current_gains(self) -> List[int]:
        return list(self.gains) if self.enabled else [0] * EQ_BANDS


@dataclass(eq=False)
class PlayEvent:
    track: Track
    timestamp: int
    listened_seconds: int

    def completion_ratio(self) -> float:
        total = self.track.duration.total_seconds
        return min(1.0, self.listened_seconds / total) if total else 0.0

    def is_skip(self) -> bool:
        return self.completion_ratio() < SKIP_RATIO


@dataclass(eq=False)
class PlaybackHistory:
    events: List[PlayEvent] = field(default_factory=list)
    limit: int = HISTORY_LIMIT

    def record(self, event: PlayEvent) -> None:
        self.events.append(event)
        if len(self.events) > self.limit:
            del self.events[: len(self.events) - self.limit]

    def most_played(self, count: int) -> List[str]:
        counter = Counter(event.track.title for event in self.events)
        return [title for title, _ in counter.most_common(count)]

    def total_listening_seconds(self) -> int:
        return sum(event.listened_seconds for event in self.events)


@dataclass(eq=False)
class PlayQueue:
    tracks: List[Track] = field(default_factory=list)
    position: int = 0

    def enqueue(self, track: Track) -> None:
        self.tracks.append(track)

    def next_track(self) -> Track:
        if self.position >= len(self.tracks):
            raise EmptyQueueError("Очередь закончилась")
        self.position += 1
        return self.tracks[self.position - 1]

    def current(self) -> Track:
        if self.position == 0:
            raise EmptyQueueError("Воспроизведение ещё не началось")
        return self.tracks[self.position - 1]


@dataclass(eq=False)
class Player:
    queue: PlayQueue = field(default_factory=PlayQueue)
    history: PlaybackHistory = field(default_factory=PlaybackHistory)
    volume: int = DEFAULT_VOLUME
    playing: bool = False

    def play_next(self) -> str:
        track = self.queue.next_track()
        track.register_play()
        self.playing = True
        return track.display_name()

    def finish(self, timestamp: int) -> None:
        track = self.queue.current()
        self.history.record(PlayEvent(track, timestamp, track.duration.total_seconds))
        self.playing = False

    def set_volume(self, volume: int) -> None:
        if not MIN_VOLUME <= volume <= MAX_VOLUME:
            raise InvalidVolumeError("Громкость вне диапазона")
        self.volume = volume
