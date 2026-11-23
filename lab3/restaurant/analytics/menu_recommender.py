from __future__ import annotations

from datetime import date

from restaurant.exceptions import InvalidDataError
from restaurant.guests.customer import Customer
from restaurant.inventory.inventory import Inventory
from restaurant.menu.dish import Dish
from restaurant.menu.menu import Menu


class MenuRecommender:
    def __init__(self, menu: Menu) -> None:
        self.menu = menu

    def recommend(
        self,
        customer: Customer,
        limit: int = 5,
        inventory: Inventory | None = None,
        today: date | None = None,
    ) -> list[Dish]:
        if limit <= 0:
            raise InvalidDataError("Количество рекомендаций должно быть положительным")
        candidates = [dish for dish in self.menu.all_dishes() if customer.can_eat(dish) and not dish.is_stopped]
        if inventory is not None and today is not None:
            candidates = [dish for dish in candidates if dish.is_available(inventory, today)]
        candidates.sort(key=lambda dish: (-customer.profile.times_ordered(dish.name), dish.price, dish.name))
        return candidates[:limit]
