from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from .catalog import Duration
from .constants import (
    BITS_PER_BYTE,
    BITS_PER_KILOBIT,
    BYTES_PER_MB,
    CD_SAMPLE_RATE_HZ,
    HIGH_BITRATE_KBPS,
    MAX_PLAYLIST_SIZE,
    MAX_TITLE_LENGTH,
    MAX_YEAR,
    MIN_YEAR,
    STANDARD_BITRATE_KBPS,
)
from .exceptions import (
    DuplicateTrackError,
    InvalidAudioFormatError,
    InvalidTrackDataError,
    ItemNotFoundError,
    StorageFullError,
)
from .people import Artist

if TYPE_CHECKING:
    from .services import SearchCriteria, SearchEngine


@dataclass(eq=False)
class AudioFormat:
    name: str
    extension: str
    lossless: bool
    max_bitrate_kbps: int

    def supports_bitrate(self, bitrate_kbps: int) -> bool:
        return 0 < bitrate_kbps <= self.max_bitrate_kbps

    def estimate_size(self, duration_seconds: int, bitrate_kbps: int) -> int:
        return duration_seconds * bitrate_kbps * BITS_PER_KILOBIT // BITS_PER_BYTE


@dataclass(eq=False)
class AudioFile:
    path: str
    format: AudioFormat
    size_bytes: int
    bitrate_kbps: int
    sample_rate_hz: int = CD_SAMPLE_RATE_HZ

    def size_mb(self) -> float:
        return self.size_bytes / BYTES_PER_MB

    def validate(self) -> None:
        if not self.path.lower().endswith("." + self.format.extension):
            raise InvalidAudioFormatError("Расширение не совпадает с форматом")
        if not self.format.supports_bitrate(self.bitrate_kbps):
            raise InvalidAudioFormatError("Недопустимый битрейт для формата")

    def quality_label(self) -> str:
        if self.format.lossless:
            return "lossless"
        if self.bitrate_kbps >= HIGH_BITRATE_KBPS:
            return "high"
        if self.bitrate_kbps >= STANDARD_BITRATE_KBPS:
            return "standard"
        return "low"


@dataclass(eq=False)
class Track:
    title: str
    artist: Artist
    duration: Duration
    genre: str
    audio_file: AudioFile
    year: int
    tags: List[str] = field(default_factory=list)
    play_count: int = 0

    def validate(self) -> None:
        if not self.title.strip() or len(self.title) > MAX_TITLE_LENGTH:
            raise InvalidTrackDataError("Некорректное название трека")
        if not MIN_YEAR <= self.year <= MAX_YEAR:
            raise InvalidTrackDataError("Некорректный год выпуска")

    def add_tag(self, tag: str) -> None:
        if tag.strip().lower() not in (known.lower() for known in self.tags):
            self.tags.append(tag.strip())

    def display_name(self) -> str:
        return f"{self.artist.name} — {self.title}"

    def register_play(self) -> int:
        self.play_count += 1
        return self.play_count


@dataclass(eq=False)
class Album:
    title: str
    artist_name: str
    release_year: int
    tracks: List[Track] = field(default_factory=list)

    def add_track(self, track: Track) -> None:
        track.validate()
        if any(existing.title == track.title for existing in self.tracks):
            raise DuplicateTrackError(f"Трек «{track.title}» уже в альбоме")
        self.tracks.append(track)

    def find_track(self, title: str) -> Track:
        for track in self.tracks:
            if track.title == title:
                return track
        raise ItemNotFoundError(f"Трек «{title}» не найден в альбоме")

    def total_duration(self) -> Duration:
        return Duration(sum(track.duration.total_seconds for track in self.tracks))


@dataclass(eq=False)
class Compilation(Album):
    theme: str = ""

    def is_various_artists(self) -> bool:
        return len({track.artist.name for track in self.tracks}) > 1


@dataclass(eq=False)
class Playlist:
    name: str
    owner: str
    tracks: List[Track] = field(default_factory=list)
    max_size: int = MAX_PLAYLIST_SIZE

    def add_track(self, track: Track) -> None:
        if len(self.tracks) >= self.max_size:
            raise StorageFullError("Плейлист заполнен")
        self.tracks.append(track)

    def remove_track(self, track: Track) -> None:
        if not any(item is track for item in self.tracks):
            raise ItemNotFoundError("Трека нет в плейлисте")
        self.tracks.remove(track)

    def total_duration(self) -> Duration:
        return Duration(sum(track.duration.total_seconds for track in self.tracks))

    def shuffle(self, rng: random.Random) -> None:
        rng.shuffle(self.tracks)


@dataclass(eq=False)
class SmartPlaylist(Playlist):
    criteria: Optional[SearchCriteria] = None

    def refresh(self, engine: SearchEngine) -> int:
        self.tracks.clear()
        if self.criteria is None:
            return 0
        self.tracks.extend(engine.search(self.criteria)[: self.max_size])
        return len(self.tracks)


@dataclass(eq=False)
class Discography:
    artist_name: str
    release_years: List[int] = field(default_factory=list)

    def add_release_year(self, year: int) -> None:
        if not MIN_YEAR <= year <= MAX_YEAR:
            raise InvalidTrackDataError("Некорректный год выпуска")
        self.release_years.append(year)

    def first_release_year(self) -> Optional[int]:
        return min(self.release_years) if self.release_years else None
