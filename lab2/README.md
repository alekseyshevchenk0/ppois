# Audio Collection — Python OOP Project

A Python object-oriented project that models a personal audio collection. It includes
artists and bands, tracks, albums, playlists, audio files and formats, physical media,
podcasts and audiobooks, a player with a queue and equalizer, playback history, ratings,
purchases and subscriptions, search, import and export, backups, recommendations and statistics.

The project is organised as a Python package (`audio_collection`) with a separate console
interface (`cli`). It uses in-memory objects and collections; no database or external
service is required.

---

## Features

- Store tracks and albums with validation of title, year, audio format and bitrate.
- Track free space on a storage device when tracks are added or removed.
- Search tracks by text, genre, release years and compression type; build smart playlists.
- Keep a play queue, playback history and player volume.
- Rate tracks, write album reviews, keep favorites and a wishlist.
- Buy albums from a wallet, manage subscriptions, sell concert tickets.
- Account for physical media (vinyl, CDs) on shelves, with wear and residual value.
- Manage podcasts and audiobooks: episodes, chapters, finding a chapter by position.
- Import tracks from file names, convert formats, find duplicates.
- Export the collection to CSV and M3U, make backups, get recommendations.

---

## Classes by module

The model contains **60 classes** in 11 modules of the `audio_collection` package, plus 12 custom exception classes.

### `catalog` — Reference entities

| Class | Main data | Key behaviours |
|---|---|---|
| `Duration` | `total_seconds` | `from_minutes_seconds` — Creates a duration from minutes and seconds<br>`format` — Formats the duration as MM:SS |
| `Genre` | `name`, `parent` | `full_path` — Returns the genre path from the root of the hierarchy |
| `Tag` | `name`, `weight` | — |
| `Label` | `name`, `founded_year` | `age` — Age of the label in years |
| `CoverArt` | `image_path`, `width`, `height` | `is_high_quality` — Checks that both sides reach the minimum size |
| `Lyrics` | `text`, `language` | `word_count` — Number of words in the text<br>`censored` — Returns the text with banned words masked |

### `people` — People

| Class | Main data | Key behaviours |
|---|---|---|
| `Artist` | `name`, `birth_year`, `genres` | `age` — Artist's age in the given year |
| `Band` *(extends `Artist`)* | `members`, `formed_year` | `add_member` — Adds a band member |
| `Composer` | `name`, `country` | — |
| `Collector` | `username`, `email`, `joined_year`, `password_hash`, `subscription` | `has_valid_email` — Checks the e-mail address format<br>`set_password` — Sets the password after checking its strength<br>`check_password` — Checks a password against the stored hash<br>`has_active_subscription` — Checks for an active subscription |

### `media` — Media

| Class | Main data | Key behaviours |
|---|---|---|
| `AudioFormat` | `name`, `extension`, `lossless`, `max_bitrate_kbps` | `supports_bitrate` — Checks whether the bitrate is valid for the format<br>`estimate_size` — Estimates the file size in bytes |
| `AudioFile` | `path`, `format`, `size_bytes`, `bitrate_kbps`, `sample_rate_hz` | `size_mb` — File size in megabytes<br>`validate` — Checks that path, format and bitrate are consistent<br>`quality_label` — Text label for the sound quality |
| `Track` | `title`, `artist`, `duration`, `genre`, `audio_file`, `year`, `tags`, `play_count` | `validate` — Validates the title and the year<br>`add_tag` — Adds a tag unless it is already present<br>`display_name` — Display name: "Artist — Track"<br>`register_play` — Increments the play counter |
| `Album` | `title`, `artist_name`, `release_year`, `tracks` | `add_track` — Adds a track to the album<br>`find_track` — Finds a track by title<br>`total_duration` — Total duration of the album |
| `Compilation` *(extends `Album`)* | `theme` | `is_various_artists` — Checks that the compilation has more than one artist |
| `Playlist` | `name`, `owner`, `tracks`, `max_size` | `add_track` — Adds a track to the playlist<br>`remove_track` — Removes a track from the playlist<br>`total_duration` — Total duration of the playlist<br>`shuffle` — Shuffles the tracks |
| `SmartPlaylist` *(extends `Playlist`)* | `criteria` | `refresh` — Refills the playlist with the tracks found |
| `Discography` | `artist_name`, `release_years` | `add_release_year` — Registers an album release year<br>`first_release_year` — Year of the first release |

### `physical` — Physical media

| Class | Main data | Key behaviours |
|---|---|---|
| `PhysicalMedia` | `title`, `album_title`, `condition`, `purchase_price` | `degrade` — Degrades the medium's condition, but not below the minimum<br>`depreciated_value` — Residual value of the medium after the given number of years |
| `Vinyl` *(extends `PhysicalMedia`)* | `rpm` | `is_lp` — Checks that this is a long-playing record |
| `CompactDisc` *(extends `PhysicalMedia`)* | `disc_count` | `is_boxset` — Checks that the edition is a multi-disc box set |
| `Shelf` | `label`, `capacity`, `items` | `place` — Puts a medium on the shelf<br>`free_slots` — Number of free slots<br>`total_value` — Total purchase price of the media |

### `spoken` — Spoken content

| Class | Main data | Key behaviours |
|---|---|---|
| `Episode` | `title`, `number`, `season`, `duration_seconds` | `label` — Label like S01E02 followed by the title |
| `Podcast` | `title`, `host`, `episodes` | `add_episode` — Adds an episode after validating its number and season<br>`latest_episode` — Latest episode by season and number<br>`total_seconds` — Total duration of all episodes |
| `Chapter` | `title`, `number`, `duration_seconds` | `is_long` — Checks that the chapter reaches the long-chapter threshold |
| `Audiobook` | `title`, `author`, `chapters` | `add_chapter` — Adds a chapter<br>`chapter_at` — Chapter playing at the given second |

### `playback` — Playback

| Class | Main data | Key behaviours |
|---|---|---|
| `EqualizerPreset` | `name`, `gains` | `validate` — Validates the number of bands and the gain range |
| `Equalizer` | `gains`, `enabled` | `apply_gains` — Applies a validated set of gains<br>`current_gains` — Current gain per band |
| `PlayEvent` | `track`, `timestamp`, `listened_seconds` | `completion_ratio` — Fraction of the track that was listened to<br>`is_skip` — Checks that the track was skipped |
| `PlaybackHistory` | `events`, `limit` | `record` — Records the event and drops the oldest ones above the limit<br>`most_played` — Titles of the most frequently played tracks<br>`total_listening_seconds` — Total listening time |
| `PlayQueue` | `tracks`, `position` | `enqueue` — Appends a track to the end of the queue<br>`next_track` — Takes the next track<br>`current` — Current (most recently started) track |
| `Player` | `queue`, `history`, `volume`, `playing` | `play_next` — Starts the next queued track and returns its display name<br>`finish` — Finishes the current track and records a full listen<br>`set_volume` — Sets the volume |

### `social` — Ratings and favorites

| Class | Main data | Key behaviours |
|---|---|---|
| `Rating` | `track_title`, `collector`, `score` | `validate` — Validates the rating range<br>`is_positive` — Checks that the rating is positive |
| `Review` | `author`, `album_title`, `text`, `score` | `validate` — Validates the score and that the text is not empty<br>`summary` — Short summary of the review |
| `Favorites` | `owner`, `track_titles` | `add_track` — Adds a track to favorites, returns False for a repeat |
| `Wishlist` | `owner`, `budget`, `album_titles` | `fits_budget` — Checks that the list fits the budget |

### `commerce` — Commerce

| Class | Main data | Key behaviours |
|---|---|---|
| `Subscription` | `plan`, `monthly_price`, `start_day`, `duration_days` | `is_active` — Checks whether the subscription is active on the given day<br>`require_active` — Raises an exception if the subscription is inactive<br>`total_cost` — Total cost of the subscription for its whole term |
| `Wallet` | `owner`, `balance` | `deposit` — Tops up the wallet<br>`withdraw` — Withdraws funds |
| `Payment` | `payer`, `amount`, `completed` | `process` — Processes the payment and returns the remaining balance |
| `Purchase` | `buyer`, `album_title`, `price` | `complete` — Pays for the purchase from the wallet<br>`apply_discount` — Applies a discount and returns the new price |
| `Venue` | `name`, `capacity` | `is_large` — Checks that the venue is large |
| `Concert` | `title`, `artist_name`, `venue`, `ticket_price`, `tickets_sold` | `sell_ticket` — Sells tickets and returns the revenue from the sale |

### `collection` — Collection and storage

| Class | Main data | Key behaviours |
|---|---|---|
| `StorageDevice` | `name`, `capacity_bytes`, `used_bytes` | `free_bytes` — Free space in bytes<br>`reserve` — Reserves space on the device<br>`release` — Releases space on the device |
| `AudioCollection` | `owner`, `storage`, `tracks`, `albums` | `add_track` — Adds a track and reserves space for its file<br>`has_track` — Checks whether the artist's track is present<br>`find_track` — Finds a track by title<br>`remove_track` — Removes a track and frees its space<br>`add_album` — Adds an album and its new tracks, returns the number of new tracks<br>`total_duration` — Total duration of the collection |

### `services` — Services

| Class | Main data | Key behaviours |
|---|---|---|
| `SearchCriteria` | `text`, `genre`, `min_year`, `max_year`, `lossless_only` | `matches` — Checks a track against all criteria |
| `SearchEngine` | `collection` | `search` — Searches tracks by criteria<br>`by_artist` — Tracks of an artist |
| `DuplicateFinder` | `collection`, `tolerance_seconds` | `find_duplicates` — Finds duplicate pairs (titles of both tracks)<br>`remove_duplicates` — Removes the second copy of each duplicate and returns how many were removed |
| `FormatConverter` | `target_format`, `target_bitrate` | `can_convert` — Checks whether conversion is possible without a pointless upgrade<br>`convert` — Creates the description of the converted file |
| `MetadataExtractor` | `known_formats` | `detect_format` — Detects the format by file extension<br>`extract_title` — Extracts the track title from a file name |
| `Importer` | `extractor`, `default_artist_name`, `default_genre` | `import_file` — Builds a track from a file description |
| `Exporter` | `collection`, `delimiter` | `to_csv` — Exports the tracks to CSV<br>`to_m3u` — Exports the whole collection as an M3U playlist |
| `BackupSnapshot` | `created_day`, `track_titles`, `total_bytes` | `contains` — Checks whether a track is in the snapshot |
| `BackupService` | `collection`, `target`, `last_backup_day`, `interval_days` | `needs_backup` — Checks whether it is time to make a backup<br>`create_snapshot` — Creates a backup and reserves space on the target device<br>`missing_titles` — Titles of snapshot tracks that are missing from the collection |
| `RecommendationEngine` | `collection` | `favorite_genre` — Genre with the most plays<br>`recommend` — Titles of unplayed tracks of the favorite genre |
| `StatisticsService` | `collection` | `genre_distribution` — Number of tracks per genre<br>`total_size_mb` — Total size of the collection in megabytes<br>`top_artists` — Artists with the most tracks |
| `TagEditor` | `aliases` | `canonical` — Canonical spelling of a tag<br>`normalize` — Canonicalizes tags and removes repeats, preserving order |

### `system` — System entities

| Class | Main data | Key behaviours |
|---|---|---|
| `Settings` | `theme`, `default_volume`, `autoplay` | `validate` — Validates all values |
| `Notification` | `message`, `created_day`, `level`, `read` | `is_urgent` — Checks whether the notification is urgent |
| `NotificationCenter` | `owner`, `notifications` | `notify` — Creates and stores a notification<br>`unread_count` — Number of unread notifications |
| `LoudnessAnalyzer` | `samples` | `peak` — Maximum absolute amplitude<br>`has_clipping` — Checks for signal clipping |

## Associations

An association is a relationship where a class stores another class in a field (including inside a collection) or receives it as a method parameter. Self-references and inheritance are not counted.

| From | To | Relationship |
|---|---|---|
| `Album` | `Track` | field `tracks`; parameter of `add_track` |
| `AudioCollection` | `Album` | field `albums`; parameter of `add_album` |
| `AudioCollection` | `StorageDevice` | field `storage` |
| `AudioCollection` | `Track` | field `tracks`; parameter of `add_track` |
| `AudioFile` | `AudioFormat` | field `format` |
| `Audiobook` | `Chapter` | field `chapters`; parameter of `add_chapter` |
| `BackupService` | `AudioCollection` | field `collection` |
| `BackupService` | `StorageDevice` | field `target` |
| `Band` | `Artist` | field `members`; parameter of `add_member` |
| `Collector` | `Subscription` | field `subscription` |
| `Concert` | `Venue` | field `venue` |
| `DuplicateFinder` | `AudioCollection` | field `collection` |
| `Exporter` | `AudioCollection` | field `collection` |
| `FormatConverter` | `AudioFile` | parameter of `can_convert`; parameter of `convert` |
| `FormatConverter` | `AudioFormat` | field `target_format` |
| `Importer` | `MetadataExtractor` | field `extractor` |
| `MetadataExtractor` | `AudioFormat` | field `known_formats` |
| `NotificationCenter` | `Notification` | field `notifications` |
| `PlayEvent` | `Track` | field `track` |
| `PlayQueue` | `Track` | field `tracks`; parameter of `enqueue` |
| `PlaybackHistory` | `PlayEvent` | field `events`; parameter of `record` |
| `Player` | `PlayQueue` | field `queue` |
| `Player` | `PlaybackHistory` | field `history` |
| `Playlist` | `Track` | field `tracks`; parameter of `add_track`; parameter of `remove_track` |
| `Podcast` | `Episode` | field `episodes`; parameter of `add_episode` |
| `Purchase` | `Wallet` | parameter of `complete` |
| `RecommendationEngine` | `AudioCollection` | field `collection` |
| `SearchCriteria` | `Track` | parameter of `matches` |
| `SearchEngine` | `AudioCollection` | field `collection` |
| `SearchEngine` | `SearchCriteria` | parameter of `search` |
| `Shelf` | `PhysicalMedia` | field `items`; parameter of `place` |
| `SmartPlaylist` | `SearchCriteria` | field `criteria` |
| `SmartPlaylist` | `SearchEngine` | parameter of `refresh` |
| `StatisticsService` | `AudioCollection` | field `collection` |
| `Track` | `Artist` | field `artist` |
| `Track` | `AudioFile` | field `audio_file` |
| `Track` | `Duration` | field `duration` |

## Custom exceptions

| Exception | Purpose | Raised in |
|---|---|---|
| `AudioCollectionError` | Base exception of the domain. | base class |
| `InvalidTrackDataError` | Invalid track, album, artist or duration data. | `Artist`, `Band`, `Discography`, `Duration`, `EqualizerPreset`, `Importer`, `Podcast`, `Track` |
| `InvalidRatingError` | Rating outside the allowed range. | `Rating`, `Review` |
| `InvalidAudioFormatError` | Unsupported or invalid audio format. | `AudioFile`, `FormatConverter`, `MetadataExtractor` |
| `InvalidVolumeError` | Volume outside the allowed range. | `Player`, `Settings` |
| `InvalidAmountError` | Invalid quantity, amount or settings value. | `Concert`, `PhysicalMedia`, `Purchase`, `Review`, `Settings`, `StorageDevice`, `Wallet` |
| `WeakPasswordError` | Password does not meet the requirements. | `Collector` |
| `DuplicateTrackError` | Track already exists. | `Album`, `AudioCollection` |
| `ItemNotFoundError` | Track, album or another object was not found. | `Album`, `AudioCollection`, `Audiobook`, `Playlist`, `Podcast` |
| `StorageFullError` | No room left on a device, shelf or playlist. | `Playlist`, `Shelf`, `StorageDevice` |
| `EmptyQueueError` | Play queue is empty. | `PlayQueue` |
| `PaymentError` | Insufficient funds, repeated payment or inactive subscription. | `Payment`, `Subscription`, `Wallet` |


---

## Console interface

Run `python -m cli` from the `lab2` directory. The interface lives in the `cli` package,
separately from the domain model, and works on built-in demo data. Menu labels and
messages are shown in Russian.

1. **Show collection** — list tracks with duration and quality.
2. **Import file** — create a track from a path, size, duration and year.
3. **Search track** — search by title or artist.
4. **Create playlist** — a new playlist with its first track.
5. **Play track** — start a track and record it in the history.
6. **Rate track** — a rating from 1 to 5.
7. **Statistics** — genres, size, top artists, listening time.
8. **Export to CSV** — print the collection as CSV.
9. **Buy album** — pay for an album from the store using the wallet.
10. **Top up wallet** — increase the balance.
11. **Backup** — snapshot the collection to the target device.

Data entered during a run is not persisted after the program exits.

---

## Development setup

All commands are run from the `lab2` directory.

### Create the environment and install dependencies

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

### Run the console application

```bash
python -m cli
```

### Run unit tests and check coverage

Tests are located in `tests/` and cover the domain classes and the console menu.
The 90% coverage threshold is configured in `pytest.ini`:

```bash
python -m pytest
```

The command exits with a non-zero status if a test fails or coverage is below 90%.

### Run the linter

```bash
flake8 .
```

Linter settings (maximum line length 120) are stored in `.flake8`.

## Continuous integration

The workflow `.github/workflows/lab2.yml` runs on pushes to `main`, on pull requests and
when a `lab2-v*` tag is pushed. Changes outside `lab2/` do not trigger it.

1. **`test`** — installs dependencies, runs `flake8 .` and `python -m pytest`
   (coverage must be at least 90%).
2. **`build`** — tag only: builds a standalone executable (PyInstaller) for Linux and Windows.
3. **`release`** — publishes the built files to the repository Releases.

To publish a release, merge the changes into `main` and push a tag:

```bash
git tag lab2-v1.0.0
git push origin lab2-v1.0.0
```

A release is not published if linting, tests, coverage enforcement or the build fails.

---

## Project structure

```text
lab2/
├── audio_collection/
│   ├── __init__.py
│   ├── catalog.py        # duration, genre, tag, label, cover art, lyrics
│   ├── people.py         # artists, bands, composers, collector
│   ├── media.py          # formats, files, tracks, albums, playlists
│   ├── physical.py       # vinyl, CDs, shelves
│   ├── spoken.py         # podcasts and audiobooks
│   ├── playback.py       # player, queue, equalizer, history
│   ├── social.py         # ratings, reviews, favorites, wishlist
│   ├── commerce.py       # subscriptions, wallet, payments, purchases, concerts
│   ├── collection.py     # storage device and the audio collection
│   ├── services.py       # search, import, export, backup, recommendations
│   ├── system.py         # settings, notifications, loudness analysis
│   ├── constants.py      # named constants
│   └── exceptions.py     # custom exceptions
├── cli/
│   ├── __main__.py       # entry point: python -m cli
│   ├── app.py            # menu
│   ├── demo_data.py      # demo data
│   └── state.py          # application state
├── tests/
│   ├── factories.py
│   ├── test_catalog_people.py
│   ├── test_media.py
│   ├── test_physical_spoken.py
│   ├── test_playback_social_commerce.py
│   ├── test_collection_services.py
│   └── test_cli.py
├── .flake8
├── pytest.ini
├── requirements-dev.txt
└── README.md
```

---

## Notes

- Python 3.10 or newer is required; CI uses Python 3.12.
- The domain package does not depend on the console interface: `cli` imports
  `audio_collection`, never the other way round.
- Numeric values are kept in `constants.py`; methods are shorter than 20 lines and lines
  do not exceed 120 characters.
- Unit tests cover the domain classes and the menu. A coverage percentage measures executed
  code and does not prove that every business scenario is tested.
