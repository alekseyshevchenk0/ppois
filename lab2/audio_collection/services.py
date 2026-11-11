from __future__ import annotations

import os
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .catalog import Duration
from .collection import AudioCollection, StorageDevice
from .constants import (
    BACKUP_INTERVAL_DAYS,
    BITS_PER_BYTE,
    BITS_PER_KILOBIT,
    BYTES_PER_MB,
    CSV_DELIMITER,
    DEFAULT_RECOMMENDATIONS,
    DUPLICATE_TOLERANCE_SECONDS,
    TRACK_PREFIX_PATTERN,
)
from .exceptions import InvalidAudioFormatError, InvalidTrackDataError
from .media import AudioFile, AudioFormat, Track
from .people import Artist


def are_duplicates(first: Track, second: Track, tolerance_seconds: int) -> bool:
    same_name = first.title.lower() == second.title.lower()
    same_artist = first.artist.name == second.artist.name
    gap = abs(first.duration.total_seconds - second.duration.total_seconds)
    return same_name and same_artist and gap <= tolerance_seconds


@dataclass(eq=False)
class SearchCriteria:
    text: str = ""
    genre: Optional[str] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    lossless_only: bool = False

    def matches(self, track: Track) -> bool:
        needle = self.text.lower()
        text_ok = not needle or needle in track.title.lower() or needle in track.artist.name.lower()
        genre_ok = self.genre is None or track.genre == self.genre
        after_min = self.min_year is None or track.year >= self.min_year
        before_max = self.max_year is None or track.year <= self.max_year
        quality_ok = not self.lossless_only or track.audio_file.format.lossless
        return text_ok and genre_ok and after_min and before_max and quality_ok


@dataclass(eq=False)
class SearchEngine:
    collection: AudioCollection

    def search(self, criteria: SearchCriteria) -> List[Track]:
        return [track for track in self.collection.tracks if criteria.matches(track)]

    def by_artist(self, name: str) -> List[Track]:
        return [t for t in self.collection.tracks if t.artist.name.lower() == name.lower()]


@dataclass(eq=False)
class DuplicateFinder:
    collection: AudioCollection
    tolerance_seconds: int = DUPLICATE_TOLERANCE_SECONDS

    def find_duplicates(self) -> List[Tuple[str, str]]:
        tracks = self.collection.tracks
        return [(a.title, b.title) for i, a in enumerate(tracks) for b in tracks[i + 1:]
                if are_duplicates(a, b, self.tolerance_seconds)]

    def remove_duplicates(self) -> int:
        tracks = self.collection.tracks
        extras = [b for i, a in enumerate(tracks) for b in tracks[i + 1:]
                  if are_duplicates(a, b, self.tolerance_seconds)]
        for extra in extras:
            if any(extra is track for track in tracks):
                tracks.remove(extra)
                self.collection.storage.release(extra.audio_file.size_bytes)
        return len(extras)


@dataclass(eq=False)
class FormatConverter:
    target_format: AudioFormat
    target_bitrate: int

    def can_convert(self, file: AudioFile) -> bool:
        keeps_quality = file.format.lossless or not self.target_format.lossless
        return self.target_format.supports_bitrate(self.target_bitrate) and keeps_quality

    def convert(self, file: AudioFile, duration_seconds: int) -> AudioFile:
        if not self.can_convert(file):
            raise InvalidAudioFormatError("Конвертация невозможна")
        size = self.target_format.estimate_size(duration_seconds, self.target_bitrate)
        new_path = f"{os.path.splitext(file.path)[0]}.{self.target_format.extension}"
        return AudioFile(new_path, self.target_format, size, self.target_bitrate, file.sample_rate_hz)


@dataclass(eq=False)
class MetadataExtractor:
    known_formats: List[AudioFormat] = field(default_factory=list)

    def detect_format(self, path: str) -> AudioFormat:
        extension = os.path.splitext(path)[1].lstrip(".").lower()
        for audio_format in self.known_formats:
            if audio_format.extension == extension:
                return audio_format
        raise InvalidAudioFormatError(f"Неизвестный формат: {extension or 'нет расширения'}")

    def extract_title(self, path: str) -> str:
        name = os.path.splitext(os.path.basename(path))[0]
        return re.sub(TRACK_PREFIX_PATTERN, "", name).strip()


@dataclass(eq=False)
class Importer:
    extractor: MetadataExtractor
    default_artist_name: str
    default_genre: str

    def import_file(self, path: str, size_bytes: int, duration_seconds: int, year: int) -> Track:
        if duration_seconds <= 0:
            raise InvalidTrackDataError("Длительность файла должна быть положительной")
        audio_format = self.extractor.detect_format(path)
        bitrate = size_bytes * BITS_PER_BYTE // duration_seconds // BITS_PER_KILOBIT
        audio_file = AudioFile(path, audio_format, size_bytes, bitrate)
        audio_file.validate()
        return Track(self.extractor.extract_title(path), Artist(self.default_artist_name),
                     Duration(duration_seconds), self.default_genre, audio_file, year)


@dataclass(eq=False)
class Exporter:
    collection: AudioCollection
    delimiter: str = CSV_DELIMITER

    def to_csv(self) -> str:
        rows = [self.delimiter.join(["title", "artist", "year", "duration"])]
        for track in self.collection.tracks:
            fields = [track.title, track.artist.name, str(track.year), track.duration.format()]
            rows.append(self.delimiter.join(fields))
        return "\n".join(rows)

    def to_m3u(self) -> str:
        lines = ["#EXTM3U"]
        for track in self.collection.tracks:
            lines.append(f"#EXTINF:{track.duration.total_seconds},{track.display_name()}")
            lines.append(track.audio_file.path)
        return "\n".join(lines)


@dataclass(eq=False)
class BackupSnapshot:
    created_day: int
    track_titles: List[str]
    total_bytes: int

    def contains(self, title: str) -> bool:
        return title in self.track_titles


@dataclass(eq=False)
class BackupService:
    collection: AudioCollection
    target: StorageDevice
    last_backup_day: Optional[int] = None
    interval_days: int = BACKUP_INTERVAL_DAYS

    def needs_backup(self, today: int) -> bool:
        return self.last_backup_day is None or today - self.last_backup_day >= self.interval_days

    def create_snapshot(self, today: int) -> BackupSnapshot:
        tracks = self.collection.tracks
        size = sum(track.audio_file.size_bytes for track in tracks)
        self.target.reserve(size)
        self.last_backup_day = today
        return BackupSnapshot(today, [track.title for track in tracks], size)

    def missing_titles(self, snapshot_titles: List[str]) -> List[str]:
        present = {track.title for track in self.collection.tracks}
        return [title for title in snapshot_titles if title not in present]


@dataclass(eq=False)
class RecommendationEngine:
    collection: AudioCollection

    def favorite_genre(self) -> Optional[str]:
        plays: Counter = Counter()
        for track in self.collection.tracks:
            plays[track.genre] += track.play_count
        top = plays.most_common(1)
        return top[0][0] if top and top[0][1] > 0 else None

    def recommend(self, limit: int = DEFAULT_RECOMMENDATIONS) -> List[str]:
        favorite = self.favorite_genre()
        if favorite is None:
            return []
        fresh = [t.title for t in self.collection.tracks
                 if t.genre == favorite and t.play_count == 0]
        return fresh[:limit]


@dataclass(eq=False)
class StatisticsService:
    collection: AudioCollection

    def genre_distribution(self) -> Dict[str, int]:
        return dict(Counter(track.genre for track in self.collection.tracks))

    def total_size_mb(self) -> float:
        total = sum(track.audio_file.size_bytes for track in self.collection.tracks)
        return round(total / BYTES_PER_MB, 2)

    def top_artists(self, count: int) -> List[Tuple[str, int]]:
        counter = Counter(track.artist.name for track in self.collection.tracks)
        return counter.most_common(count)


@dataclass(eq=False)
class TagEditor:
    aliases: Dict[str, str] = field(default_factory=dict)

    def canonical(self, tag: str) -> str:
        key = tag.strip().lower()
        return self.aliases.get(key, key)

    def normalize(self, tags: List[str]) -> List[str]:
        result: List[str] = []
        for tag in tags:
            name = self.canonical(tag)
            if name not in result:
                result.append(name)
        return result
