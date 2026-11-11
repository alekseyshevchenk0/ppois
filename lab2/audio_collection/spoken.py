from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .constants import LONG_CHAPTER_SECONDS
from .exceptions import InvalidTrackDataError, ItemNotFoundError


@dataclass(eq=False)
class Episode:
    title: str
    number: int
    season: int
    duration_seconds: int

    def label(self) -> str:
        return f"S{self.season:02d}E{self.number:02d} {self.title}"


@dataclass(eq=False)
class Podcast:
    title: str
    host: str
    episodes: List[Episode] = field(default_factory=list)

    def add_episode(self, episode: Episode) -> None:
        if episode.number < 1 or episode.season < 1:
            raise InvalidTrackDataError("Номер выпуска и сезона начинается с 1")
        self.episodes.append(episode)

    def latest_episode(self) -> Episode:
        if not self.episodes:
            raise ItemNotFoundError("В подкасте нет выпусков")
        return max(self.episodes, key=lambda ep: (ep.season, ep.number))

    def total_seconds(self) -> int:
        return sum(episode.duration_seconds for episode in self.episodes)


@dataclass(eq=False)
class Chapter:
    title: str
    number: int
    duration_seconds: int

    def is_long(self) -> bool:
        return self.duration_seconds >= LONG_CHAPTER_SECONDS


@dataclass(eq=False)
class Audiobook:
    title: str
    author: str
    chapters: List[Chapter] = field(default_factory=list)

    def add_chapter(self, chapter: Chapter) -> None:
        self.chapters.append(chapter)

    def chapter_at(self, position_seconds: int) -> Chapter:
        elapsed = 0
        for chapter in self.chapters:
            elapsed += chapter.duration_seconds
            if position_seconds < elapsed:
                return chapter
        raise ItemNotFoundError("Позиция за пределами книги")
