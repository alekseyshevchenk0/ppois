from audio_collection.catalog import Duration
from audio_collection.collection import AudioCollection, StorageDevice
from audio_collection.media import Album, AudioFile, AudioFormat, Track
from audio_collection.people import Artist

BIG_STORAGE = 10_000_000_000
DEFAULT_SIZE = 1_000_000
MB = 1024 * 1024


def make_format(name="MP3", extension="mp3", lossless=False, max_bitrate=320):
    return AudioFormat(name, extension, lossless, max_bitrate)


def make_file(path="/m/a.mp3", audio_format=None, size=DEFAULT_SIZE, bitrate=256):
    return AudioFile(path, audio_format or make_format(), size, bitrate)


def make_artist(name="Artist"):
    return Artist(name, 1960)


def make_track(title="Song", artist=None, seconds=200, genre="Rock", year=2000, size=DEFAULT_SIZE,
               audio_format=None):
    audio_format = audio_format or make_format()
    audio_file = make_file(f"/m/{title}.{audio_format.extension}", audio_format, size)
    return Track(title, artist or make_artist(), Duration(seconds), genre, audio_file, year)


def make_album(title="Album", artist_name="Artist", tracks=None):
    album = Album(title, artist_name, 2000)
    for track in tracks or []:
        album.add_track(track)
    return album


def make_collection(capacity=BIG_STORAGE):
    return AudioCollection("user", StorageDevice("disk", capacity))
