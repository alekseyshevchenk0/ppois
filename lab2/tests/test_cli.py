from cli.app import Console, MenuApp
from cli.demo_data import build_demo_state


def run_menu(commands, state=None):
    outputs = []
    feed = iter(commands)
    state = state or build_demo_state()
    MenuApp(state, Console(lambda prompt: next(feed), outputs.append)).run()
    return state, "\n".join(outputs)


def test_exit_and_unknown_choice():
    _, text = run_menu(["99", "0"])
    assert "Неизвестный пункт меню" in text and "До свидания" in text


def test_show_and_search():
    _, text = run_menu(["1", "3", "time", "0"])
    assert "Pink Floyd — Time" in text and "Найдено: 1" in text


def test_import_valid_and_invalid():
    state, text = run_menu(["2", "/m/03 - New.mp3", "4000000", "200", "2000",
                            "2", "/m/x.mp3", "abc", "1", "1", "0"])
    assert "Добавлен трек: Pink Floyd — New" in text
    assert "Ошибка" in text
    assert len(state.collection.tracks) == 3


def test_playlist_and_play():
    state, text = run_menu(["4", "Mix", "Time", "5", "Money", "0"])
    assert "Плейлист «Mix»: 06:53" in text and "прослушиваний: 1" in text
    assert len(state.playlists) == 1
    assert state.player.history.total_listening_seconds() == 382


def test_missing_track_reports_error():
    _, text = run_menu(["5", "Unknown", "0"])
    assert "Ошибка" in text


def test_rating():
    state, text = run_menu(["6", "Time", "5", "6", "Time", "9", "0"])
    assert "Оценка сохранена" in text and len(state.ratings) == 1
    assert text.count("Ошибка") == 1


def test_statistics_and_export():
    _, text = run_menu(["7", "8", "0"])
    assert "Жанры" in text and "title,artist,year,duration" in text


def test_buy_album_and_top_up():
    state, text = run_menu(["9", "Discovery", "9", "Nothing", "10", "5", "10", "-1", "0"])
    assert "Куплен альбом «Discovery»" in text
    assert state.wallet.balance == 15.01 and not state.store_albums
    assert text.count("Ошибка") == 2


def test_buy_without_money():
    state = build_demo_state()
    state.wallet.balance = 1.0
    _, text = run_menu(["9", "Discovery", "0"], state)
    assert "Недостаточно средств" in text


def test_backup_twice():
    _, text = run_menu(["11", "11", "0"])
    assert "Копия создана: треков 2" in text and "Копия не требуется" in text


def test_main_entry(monkeypatch, capsys):
    from cli import __main__ as entry
    monkeypatch.setattr("builtins.input", lambda prompt: "0")
    entry.main()
    assert "До свидания" in capsys.readouterr().out
