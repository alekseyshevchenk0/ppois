from typing import Callable, Dict, Optional, Tuple

from audio_collection.commerce import Purchase
from audio_collection.exceptions import AudioCollectionError, ItemNotFoundError
from audio_collection.media import Playlist
from audio_collection.services import SearchCriteria
from audio_collection.social import Rating
from cli.state import AppState

EXIT_CHOICE = "0"
MENU_TITLE = "=== Аудиоколлекция ==="


class Console:
    def __init__(self, input_func: Optional[Callable[[str], str]] = None,
                 output_func: Optional[Callable[[str], None]] = None) -> None:
        self._input = input_func or input
        self._output = output_func or print

    def ask(self, prompt: str) -> str:
        return self._input(f"{prompt}: ").strip()

    def say(self, text: str) -> None:
        self._output(text)


class MenuApp:
    def __init__(self, state: AppState, console: Console) -> None:
        self.state = state
        self.console = console
        self.actions: Dict[str, Tuple[str, Callable[[], None]]] = {
            "1": ("Показать коллекцию", self.show_tracks),
            "2": ("Импортировать файл", self.add_track),
            "3": ("Поиск трека", self.search),
            "4": ("Создать плейлист", self.create_playlist),
            "5": ("Воспроизвести трек", self.play_track),
            "6": ("Оценить трек", self.rate_track),
            "7": ("Статистика", self.show_statistics),
            "8": ("Экспорт в CSV", self.export_csv),
            "9": ("Купить альбом", self.buy_album),
            "10": ("Пополнить кошелёк", self.top_up),
            "11": ("Резервная копия", self.make_backup),
        }

    def run(self) -> None:
        while True:
            self.print_menu()
            choice = self.console.ask("Выбор")
            if choice == EXIT_CHOICE:
                self.console.say("До свидания!")
                return
            self.dispatch(choice)

    def print_menu(self) -> None:
        self.console.say(MENU_TITLE)
        for key, (title, _) in self.actions.items():
            self.console.say(f"{key}. {title}")
        self.console.say(f"{EXIT_CHOICE}. Выход")

    def dispatch(self, choice: str) -> None:
        action = self.actions.get(choice)
        if action is None:
            self.console.say("Неизвестный пункт меню")
            return
        try:
            action[1]()
        except (AudioCollectionError, ValueError) as error:
            self.console.say(f"Ошибка: {error}")

    def show_tracks(self) -> None:
        for number, track in enumerate(self.state.collection.tracks, start=1):
            quality = track.audio_file.quality_label()
            self.console.say(f"{number}. {track.display_name()} [{track.duration.format()}] {quality}")

    def add_track(self) -> None:
        path = self.console.ask("Путь к файлу")
        size = int(self.console.ask("Размер, байт"))
        seconds = int(self.console.ask("Длительность, с"))
        year = int(self.console.ask("Год"))
        track = self.state.importer.import_file(path, size, seconds, year)
        self.state.collection.add_track(track)
        self.console.say(f"Добавлен трек: {track.display_name()}")

    def search(self) -> None:
        criteria = SearchCriteria(text=self.console.ask("Что искать"))
        found = self.state.search_engine.search(criteria)
        self.console.say(f"Найдено: {len(found)}")
        for track in found:
            self.console.say(f"- {track.display_name()}")

    def create_playlist(self) -> None:
        playlist = Playlist(self.console.ask("Название плейлиста"), self.state.collection.owner)
        track = self.state.collection.find_track(self.console.ask("Трек для добавления"))
        playlist.add_track(track)
        self.state.playlists.append(playlist)
        self.console.say(f"Плейлист «{playlist.name}»: {playlist.total_duration().format()}")

    def play_track(self) -> None:
        track = self.state.collection.find_track(self.console.ask("Название трека"))
        self.state.player.queue.enqueue(track)
        self.state.player.play_next()
        self.state.player.finish(self.state.today)
        self.console.say(f"Проиграно: {track.display_name()} (прослушиваний: {track.play_count})")

    def rate_track(self) -> None:
        track = self.state.collection.find_track(self.console.ask("Название трека"))
        score = int(self.console.ask("Оценка"))
        rating = Rating(track.title, self.state.collection.owner, score)
        rating.validate()
        self.state.ratings.append(rating)
        self.console.say("Оценка сохранена")

    def show_statistics(self) -> None:
        stats = self.state.statistics
        self.console.say(f"Жанры: {stats.genre_distribution()}")
        self.console.say(f"Размер, МБ: {stats.total_size_mb()}")
        self.console.say(f"Топ исполнителей: {stats.top_artists(3)}")
        seconds = self.state.player.history.total_listening_seconds()
        self.console.say(f"Прослушано, с: {seconds}")

    def export_csv(self) -> None:
        self.console.say(self.state.exporter.to_csv())

    def buy_album(self) -> None:
        title = self.console.ask("Название альбома")
        album = self._find_store_album(title)
        price = self.state.store_price
        purchase = Purchase(self.state.collection.owner, album.title, price)
        purchase.complete(self.state.wallet)
        self.state.collection.add_album(album)
        self.state.store_albums.remove(album)
        self.console.say(f"Куплен альбом «{album.title}», баланс: {self.state.wallet.balance:.2f}")

    def _find_store_album(self, title: str):
        for album in self.state.store_albums:
            if album.title.lower() == title.lower():
                return album
        raise ItemNotFoundError(f"Альбома «{title}» нет в магазине")

    def top_up(self) -> None:
        amount = float(self.console.ask("Сумма"))
        balance = self.state.wallet.deposit(amount)
        self.console.say(f"Баланс: {balance:.2f}")

    def make_backup(self) -> None:
        if not self.state.backup.needs_backup(self.state.today):
            self.console.say("Копия не требуется")
            return
        snapshot = self.state.backup.create_snapshot(self.state.today)
        self.console.say(f"Копия создана: треков {len(snapshot.track_titles)}")
