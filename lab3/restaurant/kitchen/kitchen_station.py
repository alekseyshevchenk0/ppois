from __future__ import annotations

import math

from restaurant.exceptions import EmployeeNotAvailableError, InvalidDataError, KitchenOverloadError
from restaurant.kitchen.kitchen_ticket import KitchenTicket
from restaurant.staff.cook import Cook
from restaurant.validation import require_non_empty, require_positive


class KitchenStation:
    def __init__(self, name: str, max_wait_minutes: int) -> None:
        require_non_empty(name, "название станции")
        require_positive(max_wait_minutes, "максимальное время ожидания")
        self.name = name
        self.max_wait_minutes = max_wait_minutes
        self._cooks: list[Cook] = []
        self._tickets: list[KitchenTicket] = []

    def add_cook(self, cook: Cook) -> None:
        cook.ensure_active()
        if not cook.can_work_station(self.name):
            raise EmployeeNotAvailableError(cook.name, f"не работает на станции «{self.name}»")
        if cook in self._cooks:
            raise InvalidDataError(f"Повар «{cook.name}» уже на станции «{self.name}»")
        self._cooks.append(cook)

    def cooks_count(self) -> int:
        return len(self._cooks)

    def speed_factor(self) -> float:
        self._require_cooks()
        return sum(cook.speed_factor() for cook in self._cooks) / len(self._cooks)

    def effective_minutes(self, base_minutes: int) -> int:
        return math.ceil(base_minutes * self.speed_factor())

    def load_minutes(self) -> int:
        return sum(ticket.work_minutes for ticket in self._tickets)

    def estimate_ready_minutes(self, base_minutes: int) -> int:
        self._require_cooks()
        queue_minutes = math.ceil(self.load_minutes() / self.cooks_count())
        return queue_minutes + self.effective_minutes(base_minutes)

    def accept(self, ticket: KitchenTicket) -> None:
        if ticket.ready_in_minutes > self.max_wait_minutes:
            reason = f"ожидание {ticket.ready_in_minutes} мин превышает допустимые {self.max_wait_minutes} мин"
            raise KitchenOverloadError(self.name, reason)
        self._tickets.append(ticket)

    def release(self, ticket: KitchenTicket) -> None:
        if ticket in self._tickets:
            self._tickets.remove(ticket)

    def _require_cooks(self) -> None:
        if not self._cooks:
            raise KitchenOverloadError(self.name, "на станции нет поваров")
