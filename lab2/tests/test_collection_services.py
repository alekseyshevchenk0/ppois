import pytest

from audio_collection.catalog import Duration
from audio_collection.collection import StorageDevice
from audio_collection.exceptions import (
    DuplicateTrackError,
    InvalidAmountError,
    InvalidAudioFormatError,
    InvalidTrackDataError,
    ItemNotFoundError,
    StorageFullError,
)
from audio_collection.services import (
    BackupService,
    DuplicateFinder,
    Exporter,
    FormatConverter,
    Importer,
    MetadataExtractor,
    RecommendationEngine,
    SearchCriteria,
    SearchEngine,
    StatisticsService,
    TagEditor,
)
from audio_collection.system import LoudnessAnalyzer, Notification, NotificationCenter, Settings
from audio_collection.exceptions import InvalidVolumeError
from tests.factories import MB, make_album, make_artist, make_collection, make_file, make_format, make_track


class TestStorageDevice:
    def test_space(self):
        device = StorageDevice("d", 100)
        device.reserve(40)
        assert device.free_bytes() == 60
        device.release(500)
        assert device.used_bytes == 0
        with pytest.raises(StorageFullError):
            device.reserve(101)
        with pytest.raises(InvalidAmountError):
            device.reserve(-1)


class TestAudioCollection:
    def test_add_find_remove(self):
        collection = make_collection()
        track = make_track("Song", size=100)
        collection.add_track(track)
        assert collection.find_track("song") is track and collection.storage.used_bytes == 100
        assert collection.total_duration().total_seconds == 200
        assert collection.remove_track("Song") is track and collection.storage.used_bytes == 0
        with pytest.raises(ItemNotFoundError):
            collection.find_track("Song")

    def test_duplicate_and_full(self):
        collection = make_collection(capacity=150)
        collection.add_track(make_track("A", size=100))
        with pytest.raises(DuplicateTrackError):
            collection.add_track(make_track("a", size=10))
        with pytest.raises(StorageFullError):
            collection.add_track(make_track("B", size=100))

    def test_add_album(self):
        collection = make_collection()
        album = make_album("Wall", tracks=[make_track("A"), make_track("B")])
        assert collection.add_album(album) == 2
        assert collection.add_album(album) == 0


def filled_collection():
    collection = make_collection()
    flac = make_format("FLAC", "flac", True, 1411)
    one, two = make_artist("One"), make_artist("Two")
    for track in (
        make_track("Alpha", one, 300, "Rock", 1975, size=2 * MB),
        make_track("Beta", one, 100, "Jazz", 1985, size=MB),
        make_track("Gamma", two, 200, "Rock", 1999, size=3 * MB, audio_format=flac),
    ):
        collection.add_track(track)
    return collection


def test_search():
    engine = SearchEngine(filled_collection())
    assert len(engine.search(SearchCriteria())) == 3
    assert len(engine.search(SearchCriteria(text="two"))) == 1
    assert len(engine.search(SearchCriteria(genre="Rock"))) == 2
    assert len(engine.search(SearchCriteria(min_year=1980, max_year=1990))) == 1
    assert len(engine.search(SearchCriteria(lossless_only=True))) == 1
    assert len(engine.by_artist("one")) == 2


def test_duplicates():
    collection = make_collection()
    artist = make_artist()
    collection.tracks.extend([make_track("Song", artist, 200), make_track("song", artist, 201),
                              make_track("Song", artist, 250)])
    finder = DuplicateFinder(collection)
    assert finder.find_duplicates() == [("Song", "song")]
    assert finder.remove_duplicates() == 1 and len(collection.tracks) == 2


class TestConverterAndMetadata:
    def test_convert(self):
        flac = make_format("FLAC", "flac", True, 1411)
        source = make_file("/m/a.flac", flac, 5 * MB, 1411)
        result = FormatConverter(make_format(), 128).convert(source, 10)
        assert result.path == "/m/a.mp3" and result.size_bytes == 160000

    def test_refuses(self):
        lossy = make_file()
        flac = make_format("FLAC", "flac", True, 1411)
        assert not FormatConverter(flac, 1000).can_convert(lossy)
        assert not FormatConverter(make_format(), 999).can_convert(lossy)
        with pytest.raises(InvalidAudioFormatError):
            FormatConverter(flac, 1000).convert(lossy, 1)

    def test_extractor(self):
        extractor = MetadataExtractor([make_format()])
        assert extractor.detect_format("/x/Song.MP3").name == "MP3"
        assert extractor.extract_title("/x/01 - Song Name.mp3") == "Song Name"
        for bad in ("/x/a.xyz", "/x/noext"):
            with pytest.raises(InvalidAudioFormatError):
                extractor.detect_format(bad)


def test_importer():
    importer = Importer(MetadataExtractor([make_format()]), "Floyd", "Rock")
    track = importer.import_file("/x/01 - Song.mp3", 1_000_000, 100, 2000)
    assert track.title == "Song" and track.audio_file.bitrate_kbps == 80
    with pytest.raises(InvalidTrackDataError):
        importer.import_file("/x/a.mp3", 10, 0, 2000)
    with pytest.raises(InvalidAudioFormatError):
        importer.import_file("/x/a.mp3", 1_000_000_000, 10, 2000)


def test_exporter():
    exporter = Exporter(filled_collection())
    lines = exporter.to_csv().splitlines()
    assert lines[0] == "title,artist,year,duration" and len(lines) == 4
    assert exporter.to_m3u().splitlines()[0] == "#EXTM3U"


class TestBackup:
    def test_snapshot(self):
        collection = filled_collection()
        service = BackupService(collection, StorageDevice("nas", 100 * MB))
        assert service.needs_backup(1)
        snapshot = service.create_snapshot(10)
        assert snapshot.contains("Alpha") and not snapshot.contains("Nope")
        assert not service.needs_backup(12) and service.needs_backup(17)
        collection.remove_track("Beta")
        assert service.missing_titles(snapshot.track_titles) == ["Beta"]

    def test_no_space(self):
        service = BackupService(filled_collection(), StorageDevice("tiny", 10))
        with pytest.raises(StorageFullError):
            service.create_snapshot(1)


def test_recommendations_and_statistics():
    collection = filled_collection()
    engine = RecommendationEngine(collection)
    assert engine.favorite_genre() is None and engine.recommend() == []
    collection.tracks[0].register_play()
    assert engine.favorite_genre() == "Rock" and engine.recommend(5) == ["Gamma"]
    stats = StatisticsService(collection)
    assert stats.genre_distribution() == {"Rock": 2, "Jazz": 1}
    assert stats.total_size_mb() == 6.0 and stats.top_artists(1) == [("One", 2)]


def test_tag_editor():
    editor = TagEditor({"hiphop": "hip-hop"})
    assert editor.canonical(" HipHop ") == "hip-hop"
    assert editor.normalize(["HipHop", "hip-hop", "Rock"]) == ["hip-hop", "rock"]


class TestSystem:
    def test_settings(self):
        Settings().validate()
        with pytest.raises(InvalidAmountError):
            Settings(theme="neon").validate()
        with pytest.raises(InvalidVolumeError):
            Settings(default_volume=500).validate()

    def test_notifications(self):
        center = NotificationCenter("user")
        center.notify("a", 1)
        urgent = center.notify("b", 2, "urgent")
        assert urgent.is_urgent() and not Notification("x", 1).is_urgent()
        assert center.unread_count() == 2
        urgent.read = True
        assert center.unread_count() == 1

    def test_loudness(self):
        assert LoudnessAnalyzer([0, -32767]).peak() == 32767
        assert LoudnessAnalyzer([0, -32767]).has_clipping()
        assert LoudnessAnalyzer().peak() == 0 and not LoudnessAnalyzer().has_clipping()


def test_duration_total():
    assert Duration(5).total_seconds == 5
