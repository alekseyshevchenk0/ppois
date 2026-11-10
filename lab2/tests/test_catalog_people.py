import pytest

from audio_collection.catalog import CoverArt, Duration, Genre, Label, Lyrics, Tag
from audio_collection.commerce import Subscription
from audio_collection.exceptions import InvalidTrackDataError, WeakPasswordError
from audio_collection.people import Band, Collector, Composer
from tests.factories import make_artist


def test_duration():
    assert Duration.from_minutes_seconds(3, 5).total_seconds == 185
    assert Duration(185).format() == "03:05"
    with pytest.raises(InvalidTrackDataError):
        Duration(-1)


def test_genre_path():
    child = Genre("Prog", Genre("Rock"))
    assert child.full_path() == "Rock / Prog"
    assert Genre("Jazz").full_path() == "Jazz"


def test_simple_catalog_entities():
    assert Tag("chill").weight == 1
    assert Label("EMI", 1931).age(2031) == 100
    assert CoverArt("a.jpg", 600, 600).is_high_quality()
    assert not CoverArt("a.jpg", 600, 300).is_high_quality()
    lyrics = Lyrics("hello bad world", "en")
    assert lyrics.word_count() == 3
    assert lyrics.censored(["bad"]) == "hello *** world"


def test_artist_age():
    artist = make_artist()
    assert artist.age(2000) == 40
    with pytest.raises(InvalidTrackDataError):
        artist.age(1900)


def test_band_members():
    band, member = Band("Band", 1965), make_artist("M")
    band.add_member(member)
    assert band.members == [member]
    with pytest.raises(InvalidTrackDataError):
        band.add_member(member)
    assert Composer("Bach", "DE").name == "Bach"


class TestCollector:
    def test_email(self):
        assert Collector("u", "u@ex.com", 2020).has_valid_email()
        assert not Collector("u", "broken", 2020).has_valid_email()

    def test_password(self):
        user = Collector("u", "u@ex.com", 2020)
        for weak in ("short1", "onlyletters"):
            with pytest.raises(WeakPasswordError):
                user.set_password(weak)
        user.set_password("strongpass1")
        assert user.check_password("strongpass1") and not user.check_password("x")

    def test_subscription(self):
        user = Collector("u", "u@ex.com", 2020)
        assert not user.has_active_subscription(5)
        user.subscription = Subscription("premium", 9.99, 0, 30)
        assert user.has_active_subscription(5) and not user.has_active_subscription(40)
