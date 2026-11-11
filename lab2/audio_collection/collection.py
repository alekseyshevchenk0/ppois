from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .catalog import Duration
from .exceptions import DuplicateTrackError, InvalidAmountError, ItemNotFoundError, StorageFullError
from .media import Album, Track


@dataclass(eq=False)
class StorageDevice:
    name: str
    capacity_bytes: int
    used_bytes: int = 0

    def free_bytes(self) -> int:
        return self.capacity_bytes - self.used_bytes

    def reserve(self, size_bytes: int) -> None:
        if size_bytes < 0:
            raise InvalidAmountError("Размер не может быть отрицательным")
        if size_bytes > self.free_bytes():
            raise StorageFullError("Недостаточно места на носителе")
        self.used_bytes += size_bytes

    def release(self, size_bytes: int) -> None:
        """Освобождает место на носителе."""
        self.used_bytes = max(0, self.used_bytes - size_bytes)


@dataclass(eq=False)
class AudioCollection:
    owner: str
    storage: StorageDevice
    tracks: List[Track] = field(default_factory=list)
    albums: List[Album] = field(default_factory=list)

    def add_track(self, track: Track) -> None:
        track.validate()
        if self.has_track(track.title, track.artist.name):
            raise DuplicateTrackError(f"Трек «{track.title}» уже есть в коллекции")
        self.storage.reserve(track.audio_file.size_bytes)
        self.tracks.append(track)

    def has_track(self, title: str, artist_name: str) -> bool:
        return any(t.title.lower() == title.lower() and t.artist.name == artist_name
                   for t in self.tracks)

    def find_track(self, title: str) -> Track:
        for track in self.tracks:
            if track.title.lower() == title.lower():
                return track
        raise ItemNotFoundError(f"Трек «{title}» не найден")

    def remove_track(self, title: str) -> Track:
        track = self.find_track(title)
        self.tracks.remove(track)
        self.storage.release(track.audio_file.size_bytes)
        return track

    def add_album(self, album: Album) -> int:
        self.albums.append(album)
        new_tracks = [t for t in album.tracks if not self.has_track(t.title, t.artist.name)]
        for track in new_tracks:
            self.add_track(track)
        return len(new_tracks)

    def total_duration(self) -> Duration:
        return Duration(sum(track.duration.total_seconds for track in self.tracks))
