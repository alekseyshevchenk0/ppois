from __future__ import annotations

import math
from datetime import datetime, timedelta

from restaurant.orders.order import Order
from restaurant.orders.order_item import OrderItem
from restaurant.timeunits import SECONDS_IN_MINUTE


class KitchenTicket:
    def __init__(
        self, order: Order, item: OrderItem, station_name: str, created_at: datetime, work_minutes: int, ready_in_minutes: int
    ) -> None:
        self.order = order
        self.item = item
        self.station_name = station_name
        self.created_at = created_at
        self.work_minutes = work_minutes
        self.ready_in_minutes = ready_in_minutes
        self.is_done = False

    def expected_ready_at(self) -> datetime:
        return self.created_at + timedelta(minutes=self.ready_in_minutes)

    def minutes_left(self, now: datetime) -> int:
        if self.is_done:
            return 0
        seconds_left = (self.expected_ready_at() - now).total_seconds()
        return max(0, math.ceil(seconds_left / SECONDS_IN_MINUTE))

    def is_late(self, now: datetime) -> bool:
        return not self.is_done and now > self.expected_ready_at()

    def complete(self) -> None:
        self.is_done = True
