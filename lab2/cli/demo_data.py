from typing import List, Tuple

from audio_collection.catalog import Duration
from audio_collection.collection import AudioCollection, StorageDevice
from audio_collection.commerce import Wallet
from audio_collection.constants import DEFAULT_BITRATE_KBPS
from audio_collection.media import Album, AudioFile, AudioFormat, Track
from audio_collection.people import Artist, Band
from audio_collection.playback import Player
from audio_collection.services import (
    BackupService,
    Exporter,
    Importer,
    MetadataExtractor,
    SearchEngine,
    StatisticsService,
)
from cli.state import AppState

DEMO_STORAGE_BYTES = 2_000_000_000
DEMO_BACKUP_BYTES = 4_000_000_000
DEMO_WALLET_BALANCE = 20.0
DEMO_TODAY = 100
DEMO_OWNER = "aleksey"
DEMO_GENRE = "Rock"
LOSSLESS_BITRATE_KBPS = 1411
OGG_BITRATE_KBPS = 500


def build_formats() -> List[AudioFormat]:
    return [
        AudioFormat("MP3", "mp3", False, DEFAULT_BITRATE_KBPS),
        AudioFormat("FLAC", "flac", True, LOSSLESS_BITRATE_KBPS),
        AudioFormat("OGG", "ogg", False, OGG_BITRATE_KBPS),
    ]


def make_track(title: str, artist: Artist, genre: str, audio_format: AudioFormat,
               seconds: int, year: int) -> Track:
    bitrate = min(DEFAULT_BITRATE_KBPS, audio_format.max_bitrate_kbps)
    duration = Duration(seconds)
    size = audio_format.estimate_size(seconds, bitrate)
    path = f"/music/{artist.name}/{title}.{audio_format.extension}"
    return Track(title, artist, duration, genre, AudioFile(path, audio_format, size, bitrate), year)


def build_collection() -> Tuple[AudioCollection, str, Artist]:
    mp3, flac, _ = build_formats()
    rock = DEMO_GENRE
    floyd = Band("Pink Floyd", 1965, [rock], formed_year=1965)
    collection = AudioCollection(DEMO_OWNER, StorageDevice("SSD", DEMO_STORAGE_BYTES))
    collection.add_track(make_track("Time", floyd, rock, flac, 413, 1973))
    collection.add_track(make_track("Money", floyd, rock, mp3, 382, 1973))
    return collection, rock, floyd


def build_store_album() -> Album:
    daft = Band("Daft Punk", 1993, ["Electronic"], formed_year=1993)
    track = make_track("One More Time", daft, "Electronic", build_formats()[0], 320, 2001)
    return Album("Discovery", daft.name, 2001, [track])


def build_demo_state() -> AppState:
    collection, rock, floyd = build_collection()
    player = Player()
    extractor = MetadataExtractor(build_formats())
    return AppState(
        collection=collection, player=player,
        wallet=Wallet(DEMO_OWNER, DEMO_WALLET_BALANCE),
        importer=Importer(extractor, floyd.name, rock),
        search_engine=SearchEngine(collection), exporter=Exporter(collection),
        statistics=StatisticsService(collection),
        backup=BackupService(collection, StorageDevice("NAS", DEMO_BACKUP_BYTES)),
        store_albums=[build_store_album()], today=DEMO_TODAY,
    )
