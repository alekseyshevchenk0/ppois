from __future__ import annotations

import math
from dataclasses import dataclass

from .constants import DAYS_PER_MONTH, LARGE_VENUE_CAPACITY, PERCENT
from .exceptions import InvalidAmountError, PaymentError


@dataclass(eq=False)
class Subscription:
    plan: str
    monthly_price: float
    start_day: int
    duration_days: int

    def is_active(self, today: int) -> bool:
        return self.start_day <= today < self.start_day + self.duration_days

    def require_active(self, today: int) -> None:
        if not self.is_active(today):
            raise PaymentError("Подписка неактивна")

    def total_cost(self) -> float:
        months = math.ceil(self.duration_days / DAYS_PER_MONTH)
        return round(months * self.monthly_price, 2)


@dataclass(eq=False)
class Wallet:
    owner: str
    balance: float = 0.0

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise InvalidAmountError("Сумма пополнения должна быть положительной")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise InvalidAmountError("Сумма списания должна быть положительной")
        if self.balance < amount:
            raise PaymentError("Недостаточно средств")
        self.balance -= amount
        return self.balance


@dataclass(eq=False)
class Payment:
    payer: str
    amount: float
    completed: bool = False

    def process(self, balance: float) -> float:
        if self.completed:
            raise PaymentError("Платёж уже проведён")
        if balance < self.amount:
            raise PaymentError("Недостаточно средств")
        self.completed = True
        return balance - self.amount


@dataclass(eq=False)
class Purchase:
    buyer: str
    album_title: str
    price: float

    def complete(self, wallet: Wallet) -> Payment:
        payment = Payment(self.buyer, self.price)
        wallet.balance = payment.process(wallet.balance)
        return payment

    def apply_discount(self, percent: int) -> float:
        if not 0 <= percent <= PERCENT:
            raise InvalidAmountError("Скидка вне диапазона")
        self.price = round(self.price * (PERCENT - percent) / PERCENT, 2)
        return self.price


@dataclass(eq=False)
class Venue:
    name: str
    capacity: int

    def is_large(self) -> bool:
        return self.capacity >= LARGE_VENUE_CAPACITY


@dataclass(eq=False)
class Concert:
    title: str
    artist_name: str
    venue: Venue
    ticket_price: float
    tickets_sold: int = 0

    def sell_ticket(self, count: int) -> float:
        remaining = self.venue.capacity - self.tickets_sold
        if count <= 0 or count > remaining:
            raise InvalidAmountError("Нельзя продать такое число билетов")
        self.tickets_sold += count
        return round(count * self.ticket_price, 2)
