import random

import pytest

from audio_collection.catalog import Duration
from audio_collection.exceptions import (
    DuplicateTrackError,
    InvalidAudioFormatError,
    InvalidTrackDataError,
    ItemNotFoundError,
    StorageFullError,
)
from audio_collection.media import Compilation, Discography, Playlist, SmartPlaylist
from audio_collection.services import SearchCriteria, SearchEngine
from tests.factories import make_album, make_artist, make_collection, make_file, make_format, make_track


def test_audio_format():
    mp3 = make_format()
    assert mp3.supports_bitrate(320) and not mp3.supports_bitrate(321) and not mp3.supports_bitrate(0)
    assert mp3.estimate_size(10, 80) == 100000


class TestAudioFile:
    def test_size_and_validate(self):
        file = make_file(size=1024 * 1024)
        assert file.size_mb() == 1.0
        file.validate()
        with pytest.raises(InvalidAudioFormatError):
            make_file(path="/m/a.flac").validate()
        with pytest.raises(InvalidAudioFormatError):
            make_file(bitrate=999).validate()

    @pytest.mark.parametrize("bitrate,label", [(320, "high"), (128, "standard"), (64, "low")])
    def test_quality(self, bitrate, label):
        assert make_file(bitrate=bitrate).quality_label() == label

    def test_lossless(self):
        flac = make_format("FLAC", "flac", True, 1411)
        assert make_file("/m/a.flac", flac).quality_label() == "lossless"


class TestTrack:
    def test_validate(self):
        make_track().validate()
        with pytest.raises(InvalidTrackDataError):
            make_track(title=" ").validate()
        with pytest.raises(InvalidTrackDataError):
            make_track(year=1500).validate()

    def test_tags_name_plays(self):
        track = make_track()
        track.add_tag("Chill")
        track.add_tag("chill ")
        assert track.tags == ["Chill"]
        assert track.display_name() == "Artist — Song"
        assert track.register_play() == 1


class TestAlbum:
    def test_tracks(self):
        album = make_album(tracks=[make_track("A", seconds=100), make_track("B", seconds=50)])
        assert album.find_track("A").title == "A"
        assert album.total_duration().total_seconds == 150
        with pytest.raises(ItemNotFoundError):
            album.find_track("Z")
        with pytest.raises(DuplicateTrackError):
            album.add_track(make_track("A"))

    def test_compilation(self):
        compilation = Compilation("Hits", "Various", 2000)
        compilation.add_track(make_track("A", make_artist("One")))
        assert not compilation.is_various_artists()
        compilation.add_track(make_track("B", make_artist("Two")))
        assert compilation.is_various_artists()


class TestPlaylist:
    def test_operations(self):
        playlist, track = Playlist("mix", "user", max_size=2), make_track(seconds=30)
        playlist.add_track(track)
        playlist.add_track(make_track("B", seconds=20))
        assert playlist.total_duration().total_seconds == 50
        with pytest.raises(StorageFullError):
            playlist.add_track(make_track("C"))
        playlist.shuffle(random.Random(1))
        playlist.remove_track(track)
        with pytest.raises(ItemNotFoundError):
            playlist.remove_track(track)

    def test_smart_playlist(self):
        collection = make_collection()
        collection.add_track(make_track("A", genre="Rock"))
        collection.add_track(make_track("B", genre="Pop"))
        engine = SearchEngine(collection)
        smart = SmartPlaylist("rock", "user", criteria=SearchCriteria(genre="Rock"))
        assert smart.refresh(engine) == 1
        smart.criteria = None
        assert smart.refresh(engine) == 0


def test_discography():
    discography = Discography("Artist")
    assert discography.first_release_year() is None
    discography.add_release_year(1999)
    discography.add_release_year(1975)
    assert discography.first_release_year() == 1975
    with pytest.raises(InvalidTrackDataError):
        discography.add_release_year(1500)
    assert Duration(1).total_seconds == 1
