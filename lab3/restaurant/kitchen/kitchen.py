from __future__ import annotations

from datetime import datetime

from restaurant.exceptions import DishUnavailableError, InvalidDataError, KitchenOverloadError, OrderNotFoundError
from restaurant.inventory.inventory import Inventory
from restaurant.kitchen.kitchen_station import KitchenStation
from restaurant.kitchen.kitchen_ticket import KitchenTicket
from restaurant.menu.dish import Dish
from restaurant.orders.order import Order
from restaurant.orders.order_item import OrderItem


class Kitchen:
    def __init__(self, inventory: Inventory) -> None:
        self.inventory = inventory
        self._stations: dict[str, KitchenStation] = {}
        self._tickets: list[KitchenTicket] = []

    def add_station(self, station: KitchenStation) -> None:
        if station.name in self._stations:
            raise InvalidDataError(f"Станция «{station.name}» уже есть на кухне")
        self._stations[station.name] = station

    def station_for(self, dish: Dish) -> KitchenStation:
        name = dish.recipe.station
        if name not in self._stations:
            raise InvalidDataError(f"На кухне нет станции «{name}»")
        return self._stations[name]

    def estimate_order_minutes(self, order: Order) -> int:
        estimates = [self.station_for(item.dish).estimate_ready_minutes(item.cooking_minutes()) for item in order.items]
        return max(estimates, default=0)

    def accept_order(self, order: Order, now: datetime) -> list[KitchenTicket]:
        order.validate_for_kitchen()
        created: list[KitchenTicket] = []
        try:
            for item in order.items:
                self._check_stock(item, now)
                created.append(self._create_ticket(order, item, now))
        except (KitchenOverloadError, DishUnavailableError):
            self._rollback(created)
            raise
        order.send_to_kitchen()
        return created

    def finish_ticket(self, ticket: KitchenTicket, now: datetime) -> None:
        recipe = ticket.item.dish.recipe
        self.inventory.consume_all(recipe.requirements_for(ticket.item.quantity), now.date())
        ticket.complete()
        self._stations[ticket.station_name].release(ticket)
        if all(known.is_done for known in self.tickets_of(ticket.order.number)):
            ticket.order.mark_ready()

    def tickets_of(self, order_number: int) -> list[KitchenTicket]:
        found = [ticket for ticket in self._tickets if ticket.order.number == order_number]
        if not found:
            raise OrderNotFoundError(order_number)
        return found

    def order_minutes_left(self, order_number: int, now: datetime) -> int:
        return max(ticket.minutes_left(now) for ticket in self.tickets_of(order_number))

    def late_tickets(self, now: datetime) -> list[KitchenTicket]:
        return [ticket for ticket in self._tickets if ticket.is_late(now)]

    def station_loads(self) -> dict[str, int]:
        return {name: station.load_minutes() for name, station in self._stations.items()}

    def _check_stock(self, item: OrderItem, now: datetime) -> None:
        missing = item.dish.recipe.missing_for(self.inventory, now.date(), item.quantity)
        if missing:
            names = ", ".join(sorted(ingredient.name for ingredient in missing))
            raise DishUnavailableError(item.dish.name, f"не хватает продуктов: {names}")

    def _create_ticket(self, order: Order, item: OrderItem, now: datetime) -> KitchenTicket:
        station = self.station_for(item.dish)
        base_minutes = item.cooking_minutes()
        work_minutes = station.effective_minutes(base_minutes)
        ticket = KitchenTicket(order, item, station.name, now, work_minutes, station.estimate_ready_minutes(base_minutes))
        station.accept(ticket)
        self._tickets.append(ticket)
        return ticket

    def _rollback(self, created: list[KitchenTicket]) -> None:
        for ticket in created:
            self._stations[ticket.station_name].release(ticket)
            self._tickets.remove(ticket)
