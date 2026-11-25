from datetime import date, timedelta

from restaurant.inventory.inventory import Inventory
from restaurant.inventory.storage import InventoryStorage


def test_storage_preserves_batch_date_and_quantity(tmp_path, milk) -> None:
    path = tmp_path / "data" / "inventory.json"
    original = Inventory()
    received_on = date(2026, 11, 1)
    original.receive(milk, 125.5, received_on)
    InventoryStorage(path).save(original)

    restored = Inventory()
    assert InventoryStorage(path).load(restored, {milk.name: milk})

    batch = restored.batches[0]
    assert batch.ingredient == milk
    assert batch.quantity == 125.5
    assert batch.received_on == received_on
    assert batch.expiry_date() == received_on + timedelta(days=milk.shelf_life_days)


def test_storage_returns_false_when_file_does_not_exist(tmp_path, milk) -> None:
    storage = InventoryStorage(tmp_path / "missing.json")
    assert not storage.load(Inventory(), {milk.name: milk})


def test_inventory_change_callback_is_called(milk) -> None:
    inventory = Inventory()
    changes = []
    inventory.set_change_callback(lambda: changes.append(True))
    inventory.receive(milk, 100, date(2026, 11, 1))
    assert changes == [True]


def test_inventory_path_uses_xdg_data_home(monkeypatch) -> None:
    import sys
    from pathlib import Path

    from restaurant.__main__ import _get_inventory_path

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", "/tmp/user-data")

    assert _get_inventory_path() == Path(
        "/tmp/user-data/RestaurantApp/inventory.json"
    )


def test_inventory_path_uses_linux_default_when_xdg_is_not_set(monkeypatch) -> None:
    import sys
    from pathlib import Path

    from restaurant.__main__ import _get_inventory_path

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: Path("/home/test"))

    assert _get_inventory_path() == Path(
        "/home/test/.local/share/RestaurantApp/inventory.json"
    )


def test_inventory_path_uses_windows_local_app_data(monkeypatch) -> None:
    import sys

    from restaurant.__main__ import _get_inventory_path

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", "C:/Users/Test/AppData/Local")

    assert str(_get_inventory_path()) == (
        "C:/Users/Test/AppData/Local/RestaurantApp/inventory.json"
    )
