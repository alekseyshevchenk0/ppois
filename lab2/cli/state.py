from dataclasses import dataclass, field
from typing import List

from audio_collection.collection import AudioCollection
from audio_collection.constants import DEFAULT_ALBUM_PRICE
from audio_collection.commerce import Wallet
from audio_collection.media import Album, Playlist
from audio_collection.playback import Player
from audio_collection.services import (
    BackupService,
    Exporter,
    Importer,
    SearchEngine,
    StatisticsService,
)
from audio_collection.social import Rating


@dataclass
class AppState:
    collection: AudioCollection
    player: Player
    wallet: Wallet
    importer: Importer
    search_engine: SearchEngine
    exporter: Exporter
    statistics: StatisticsService
    backup: BackupService
    store_albums: List[Album] = field(default_factory=list)
    ratings: List[Rating] = field(default_factory=list)
    playlists: List[Playlist] = field(default_factory=list)
    today: int = 0
    store_price: float = DEFAULT_ALBUM_PRICE
