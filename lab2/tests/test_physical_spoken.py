import pytest

from audio_collection.exceptions import InvalidAmountError, InvalidTrackDataError, ItemNotFoundError, StorageFullError
from audio_collection.physical import CompactDisc, PhysicalMedia, Shelf, Vinyl
from audio_collection.spoken import Audiobook, Chapter, Episode, Podcast


def test_physical_media():
    media = PhysicalMedia("Disc", "Album", purchase_price=100.0)
    assert media.degrade(3) == 7 and media.degrade(100) == 0
    with pytest.raises(InvalidAmountError):
        media.degrade(-1)
    assert media.depreciated_value(2) == 90.0 and media.depreciated_value(100) == 0.0


def test_vinyl_and_cd():
    vinyl = Vinyl("LP", "Album")
    assert vinyl.is_lp()
    vinyl.rpm = 45
    assert not vinyl.is_lp()
    assert CompactDisc("CD", "Album", disc_count=3).is_boxset()
    assert not CompactDisc("CD", "Album").is_boxset()


def test_shelf():
    shelf = Shelf("A", capacity=1)
    shelf.place(PhysicalMedia("Disc", "Album", purchase_price=5.5))
    assert shelf.free_slots() == 0 and shelf.total_value() == 5.5
    with pytest.raises(StorageFullError):
        shelf.place(PhysicalMedia("Other", "Album"))


class TestPodcast:
    def test_episodes(self):
        podcast = Podcast("Pod", "host")
        with pytest.raises(ItemNotFoundError):
            podcast.latest_episode()
        podcast.add_episode(Episode("A", 1, 1, 100))
        podcast.add_episode(Episode("B", 1, 2, 50))
        assert podcast.latest_episode().title == "B"
        assert podcast.total_seconds() == 150
        assert podcast.episodes[1].label() == "S02E01 B"

    def test_invalid_episode(self):
        with pytest.raises(InvalidTrackDataError):
            Podcast("Pod", "host").add_episode(Episode("A", 0, 1, 10))


def test_audiobook():
    book = Audiobook("Book", "Author")
    book.add_chapter(Chapter("One", 1, 100))
    book.add_chapter(Chapter("Two", 2, 2000))
    assert book.chapter_at(50).number == 1 and book.chapter_at(150).number == 2
    assert book.chapters[1].is_long() and not book.chapters[0].is_long()
    with pytest.raises(ItemNotFoundError):
        book.chapter_at(5000)
