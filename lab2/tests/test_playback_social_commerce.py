import pytest

from audio_collection.commerce import Concert, Payment, Purchase, Subscription, Venue, Wallet
from audio_collection.exceptions import (
    EmptyQueueError,
    InvalidAmountError,
    InvalidRatingError,
    InvalidTrackDataError,
    InvalidVolumeError,
    PaymentError,
)
from audio_collection.playback import Equalizer, EqualizerPreset, PlayEvent, PlaybackHistory, Player, PlayQueue
from audio_collection.social import Favorites, Rating, Review, Wishlist
from tests.factories import make_track


class TestEqualizer:
    def test_preset_validation(self):
        EqualizerPreset("flat").validate()
        with pytest.raises(InvalidTrackDataError):
            EqualizerPreset("bad", [0]).validate()
        with pytest.raises(InvalidTrackDataError):
            EqualizerPreset("loud", [99, 0, 0, 0, 0]).validate()

    def test_gains(self):
        equalizer = Equalizer()
        equalizer.apply_gains([5, 0, 0, 0, 0])
        assert equalizer.current_gains()[0] == 5
        equalizer.enabled = False
        assert equalizer.current_gains() == [0] * 5
        with pytest.raises(InvalidTrackDataError):
            equalizer.apply_gains([1])


def test_play_event_and_history():
    track = make_track(seconds=100)
    assert PlayEvent(track, 0, 500).completion_ratio() == 1.0
    assert PlayEvent(track, 0, 10).is_skip() and not PlayEvent(track, 0, 90).is_skip()
    assert PlayEvent(make_track(seconds=0), 0, 5).completion_ratio() == 0.0
    history = PlaybackHistory(limit=2)
    other = make_track("B")
    for item in (track, other, other):
        history.record(PlayEvent(item, 0, 10))
    assert len(history.events) == 2
    assert history.most_played(1) == ["B"]
    assert history.total_listening_seconds() == 20


def test_play_queue():
    queue, first, second = PlayQueue(), make_track("A"), make_track("B")
    with pytest.raises(EmptyQueueError):
        queue.next_track()
    with pytest.raises(EmptyQueueError):
        queue.current()
    queue.enqueue(first)
    queue.enqueue(second)
    assert queue.next_track() is first and queue.current() is first
    assert queue.next_track() is second


class TestPlayer:
    def test_play_and_finish(self):
        player, track = Player(), make_track(seconds=60)
        player.queue.enqueue(track)
        assert player.play_next() == "Artist — Song"
        assert player.playing and track.play_count == 1
        player.finish(5)
        assert not player.playing and player.history.total_listening_seconds() == 60
        with pytest.raises(EmptyQueueError):
            player.play_next()

    def test_volume(self):
        player = Player()
        player.set_volume(80)
        assert player.volume == 80
        with pytest.raises(InvalidVolumeError):
            player.set_volume(101)


def test_rating_and_review():
    assert Rating("Song", "user", 5).is_positive() and not Rating("Song", "user", 2).is_positive()
    Rating("Song", "user", 3).validate()
    with pytest.raises(InvalidRatingError):
        Rating("Song", "user", 0).validate()
    review = Review("user", "Album", "great album indeed", 5)
    review.validate()
    assert review.summary(100) == "great album indeed" and review.summary(5) == "great..."
    with pytest.raises(InvalidRatingError):
        Review("user", "Album", "text", 6).validate()
    with pytest.raises(InvalidAmountError):
        Review("user", "Album", " ", 3).validate()


def test_favorites_and_wishlist():
    favorites = Favorites("user")
    assert favorites.add_track("A") and not favorites.add_track("A")
    wishlist = Wishlist("user", 15.0, ["Disc"])
    assert wishlist.fits_budget({"Disc": 12.5}) and not wishlist.fits_budget({"Disc": 20.0})


class TestSubscription:
    def test_period_and_cost(self):
        sub = Subscription("premium", 10.0, 10, 30)
        assert sub.is_active(10) and not sub.is_active(40) and not sub.is_active(5)
        assert sub.total_cost() == 10.0
        sub.require_active(20)
        with pytest.raises(PaymentError):
            sub.require_active(50)


class TestWalletAndPurchase:
    def test_wallet(self):
        wallet = Wallet("user")
        assert wallet.deposit(10) == 10 and wallet.withdraw(4) == 6
        with pytest.raises(PaymentError):
            wallet.withdraw(100)
        with pytest.raises(InvalidAmountError):
            wallet.deposit(0)
        with pytest.raises(InvalidAmountError):
            wallet.withdraw(-1)

    def test_payment(self):
        payment = Payment("user", 5.0)
        assert payment.process(20.0) == 15.0
        with pytest.raises(PaymentError):
            payment.process(20.0)
        with pytest.raises(PaymentError):
            Payment("user", 50.0).process(1.0)

    def test_purchase(self):
        wallet = Wallet("user", 20.0)
        purchase = Purchase("user", "Album", 10.0)
        assert purchase.complete(wallet).completed and wallet.balance == 10.0
        assert purchase.apply_discount(50) == 5.0
        with pytest.raises(InvalidAmountError):
            purchase.apply_discount(101)


def test_concert():
    venue = Venue("Arena", 10)
    assert not venue.is_large() and Venue("Big", 6000).is_large()
    concert = Concert("Tour", "Artist", venue, 20.0)
    assert concert.sell_ticket(4) == 80.0
    for count in (0, 7):
        with pytest.raises(InvalidAmountError):
            concert.sell_ticket(count)
