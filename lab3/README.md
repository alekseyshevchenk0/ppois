# Restaurant Management System — Python OOP Project

A Python object-oriented project that models the daily work of a restaurant. It includes a menu and recipes, ingredients and stock batches, customers and loyalty cards, employees and shifts, tables and reservations, orders and kitchen tickets, bills and payments, suppliers and purchase orders, reviews, delivery, dynamic pricing and sales analytics.

The project is organised as a Python package (`restaurant`) with a separate console application entry point. It uses in-memory objects for the restaurant domain and JSON storage for inventory batches. No database or external service is required.

---

## Project metrics

The counts below are based on the current source code.

| Metric | Count |
|---|---:|
| Domain and application classes | **58** |
| Custom exception classes | **15** |
| All classes, including custom exceptions | **73** |
| Fields in domain and application classes | **208** |
| Public behaviour methods | **261** |
| Class associations | **111** |

Counting rules:
- The 58 domain and application classes include the console application, model classes and enums, but exclude the 15 custom exception classes.
- Fields are distinct instance attributes stored on class instances.
- Behaviour methods are public methods, excluding constructors, private methods and property accessors.
- An association is a distinct class-to-class relationship represented by a typed field or a typed method parameter. A class pair is counted once even if it appears in several methods.

---

## Features

- Manage dishes, menu categories, recipes, ingredients and nutritional information.
- Track ingredient quantities in separate stock batches, including receipt dates and expiry dates.
- Consume stock using the earliest-expiry-first approach and identify expired or soon-to-expire batches.
- Persist inventory batches between launches using a JSON file in the current user's application-data directory.
- Create and manage customer profiles, dietary preferences, allergens and loyalty cards.
- Calculate loyalty points, customer discounts and loyalty tiers.
- Create restaurant orders, add and remove order items, and track order statuses.
- Send orders to kitchen stations, estimate preparation time and monitor delayed kitchen tickets.
- Calculate bills, apply discounts, promo codes and loyalty rewards, add tips and process payments.
- Manage tables, halls, reservations, no-shows, waiting lists and seating recommendations.
- Manage employees, roles, shifts, work schedules, payroll, overtime and night bonuses.
- Work with suppliers, ingredient price lists, purchase orders and stock replenishment.
- Record food waste and prepare stock reports.
- Recommend dishes based on customer preferences and available ingredients.
- Apply dynamic pricing: happy-hour discounts, peak-hour surcharges and discounts for ingredients approaching expiry.
- Collect and moderate dish reviews.
- Manage delivery orders and courier assignments.
- Generate sales reports with revenue, average check, popular dishes and revenue by day.
- Add, edit and delete dishes through the console interface.

---

## Classes by module

### `analytics` — Pricing, recommendations, reviews and reports

| Class | Main data | Key behaviours |
|---|---|---|
| `DynamicPricer` | `happy_hours`, `happy_discount`, `peak_hours`, `peak_surcharge`, expiry discount settings | `price_for` — Calculates a dish price for a given time and stock state |
| `MenuRecommender` | `menu` | `recommend` — Recommends dishes suitable for a customer and current stock |
| `Review` | `customer`, `dish`, `rating`, `comment`, `created_on`, `status` | `approve`, `reject`, `is_visible` — Moderates and checks review visibility |
| `ReviewStatus` | Review status values | Enum for pending, approved and rejected reviews |
| `SalesReport` | `payments`, `start_date`, `end_date` | `orders_count`, `total_revenue`, `average_check`, `popular_dishes`, `revenue_by_day` — Calculates sales statistics |

### `catalog` — Ingredients and nutrition

| Class | Main data | Key behaviours |
|---|---|---|
| `Allergen` | Allergen values | Enum of supported allergens |
| `Ingredient` | `name`, `unit`, `nutrition_per_unit`, `shelf_life_days`, `allergens`, `is_animal_origin` | `contains_allergen`, `nutrition_for`, `expiry_date` — Checks allergens, calculates nutrition and expiry date |
| `NutritionInfo` | `calories`, `proteins`, `fats`, `carbs` | `scale`, `combine`, `energy_from_macros`, `is_high_protein`, `is_low_calorie` — Calculates and combines nutritional values |

### `delivery` — Delivery

| Class | Main data | Key behaviours |
|---|---|---|
| `Courier` | `transport`, `active_delivery_number`, `completed_deliveries` | `assign_delivery`, `complete_delivery`, `is_available` — Assigns and completes deliveries |
| `DeliveryOrder` | `number`, `customer`, `address`, `items`, `courier`, `status`, `delivery_fee`, `created_at` | `add_item`, `assign_courier`, `pick_up`, `deliver`, `cancel`, `subtotal`, `total` — Manages a delivery lifecycle |
| `DeliveryStatus` | Delivery status values | Enum for delivery stages |

### `guests` — Customers and loyalty

| Class | Main data | Key behaviours |
|---|---|---|
| `Customer` | `email`, `profile`, `loyalty_card`, `visits_count` | `register_visit`, `is_regular`, `attach_card`, `can_eat`, `discount_percent`, `earn_loyalty_points` — Manages customer visits, preferences and rewards |
| `GuestProfile` | `forbidden_allergens`, `is_vegetarian`, `max_dish_price`, order history | `add_allergen`, `remove_allergen`, `accepts`, `record_order`, `times_ordered`, `favorites` — Stores dietary preferences and order history |
| `LoyaltyCard` | `number`, `balance`, `lifetime_points`, `issued_on` | `earn_points`, `redeem_points`, `tier`, `discount_percent`, `points_to_next_tier` — Manages loyalty points and discounts |
| `LoyaltyTier` | Loyalty tier values | Enum for customer loyalty levels |

### `hall` — Halls, tables and reservations

| Class | Main data | Key behaviours |
|---|---|---|
| `Banquet` | `hall`, `organizer`, `guests_count`, `start`, `duration_minutes`, `price_per_guest`, reservations | `required_tables`, `confirm`, `cancel`, `total_price`, `deposit_amount` — Calculates and manages banquets |
| `Hall` | `name`, `tables`, `is_outdoor` | `add_table`, `remove_table`, `find_table`, `total_capacity`, `tables_for`, `window_tables` — Manages tables in a hall |
| `Reservation` | `guest`, `table`, `start`, `duration_minutes`, `guests_count`, arrival and cancellation state | `end_time`, `is_active`, `overlaps_with`, `cancel`, `mark_arrived`, `is_no_show` — Manages a reservation |
| `ReservationBook` | Reservations | `is_table_free`, `book`, `cancel`, `reservations_of`, `reservations_on`, `free_tables`, `no_shows`, `release_no_shows` — Checks and manages reservations |
| `SeatingPlanner` | `halls`, `reservations`, `waitlist` | `candidate_tables`, `score`, `best_table`, `seat_or_wait`, `promote_from_waitlist`, `suggest_alternative_times` — Selects suitable tables and alternatives |
| `Table` | `number`, `capacity`, `near_window`, `is_in_service` | `label`, `fits`, `wasted_seats`, `take_out_of_service`, `return_to_service` — Checks table capacity and service status |
| `Waitlist` | Waiting-list entries | `join`, `leave`, `ordered`, `position_of`, `estimated_wait_minutes`, `next_for`, `take_next_for` — Manages the waiting list |
| `WaitlistEntry` | `guest`, `guests_count`, `joined_at` | `priority`, `waited_minutes` — Calculates waiting priority and elapsed time |

### `inventory` — Stock, suppliers and waste

| Class | Main data | Key behaviours |
|---|---|---|
| `Inventory` | Stock batches, reorder levels, change callback | `receive`, `total_of`, `has_enough`, `consume`, `consume_all`, `discard_expired`, `expiring_soon`, `shortage_amounts`, `stock_report` — Manages stock and expiry |
| `InventoryStorage` | `path` | `load`, `save` — Loads and saves inventory batches in JSON |
| `PurchaseOrder` | `supplier`, `created_on`, order lines, receipt state | `for_shortages`, `add_line`, `total_cost`, `expected_delivery`, `receive_into` — Creates and receives supplier orders |
| `StockItem` | `ingredient`, `quantity`, `received_on` | `expiry_date`, `is_expired`, `days_until_expiry`, `is_empty`, `consume` — Represents an individual stock batch |
| `Supplier` | `name`, `phone`, `lead_time_days`, `price_list` | `set_price`, `supplies`, `price_of`, `quote`, `delivery_date` — Manages supplier prices and delivery estimates |
| `WasteLog` | Waste entries | `record`, `total_quantity`, `quantity_by_reason` — Records and summarizes food waste |

### `kitchen` — Kitchen stations and preparation

| Class | Main data | Key behaviours |
|---|---|---|
| `Kitchen` | `inventory`, stations, tickets | `add_station`, `station_for`, `estimate_order_minutes`, `accept_order`, `finish_ticket`, `tickets_of`, `order_minutes_left`, `late_tickets`, `station_loads` — Coordinates kitchen work |
| `KitchenStation` | `name`, `max_wait_minutes`, cooks, tickets | `add_cook`, `cooks_count`, `speed_factor`, `effective_minutes`, `load_minutes`, `estimate_ready_minutes`, `accept`, `release` — Estimates and manages station workload |
| `KitchenTicket` | `order`, `item`, `station_name`, work and ready times, completion state | `expected_ready_at`, `minutes_left`, `is_late`, `complete` — Tracks preparation of an order item |

### `menu` — Menu, dishes and recipes

| Class | Main data | Key behaviours |
|---|---|---|
| `Dish` | `name`, `price`, `recipe`, `description`, `is_stopped` | `stop`, `resume`, `change_price_by_percent`, `allergens`, `is_vegetarian`, `nutrition`, `ensure_safe_for`, `is_available`, `cook`, `days_until_stock_expires` — Validates, prices and prepares dishes |
| `Menu` | `name`, categories | `add_category`, `category`, `add_dish`, `remove_dish`, `all_dishes`, `find_dish`, `available_dishes`, `stop_list`, `dishes_safe_for`, `vegetarian_dishes`, `dishes_in_price_range`, `most_expensive_dish` — Manages the restaurant menu |
| `MenuCategory` | `name`, dishes | `add_dish`, `remove_dish`, `find_dish`, `average_price`, `cheapest_dish`, `available_dishes` — Groups and searches dishes |
| `Recipe` | `steps`, `cooking_minutes`, `portions`, `station`, ingredient requirements | `add_requirement`, `ingredients`, `requirements_for`, `allergens`, `is_vegetarian`, `nutrition_per_portion`, `cooking_time_for`, `missing_for`, `can_be_cooked` — Defines preparation and ingredient requirements |

### `orders` — Orders, bills and payments

| Class | Main data | Key behaviours |
|---|---|---|
| `Bill` | `order`, discounts, `tip`, settlement state | `apply_discount`, `apply_promo`, `apply_loyalty`, `discount_percent_total`, `discount_amount`, `total_due`, `add_tip`, `total_with_tip`, `settle`, `receipt_lines` — Calculates and settles a bill |
| `Discount` | `name`, `percent`, `min_order_amount` | `applies_to`, `amount_off` — Checks and calculates a discount |
| `Order` | `number`, `guest`, `table`, `waiter`, `items`, `status`, `created_at` | `add_item`, `remove_item`, `subtotal`, `validate_for_kitchen`, `send_to_kitchen`, `mark_ready`, `mark_served`, `mark_paid`, `cancel`, `is_closed` — Manages the order lifecycle |
| `OrderItem` | `dish`, `quantity`, `unit_price`, `note` | `total`, `change_quantity`, `increase`, `is_same_position`, `cooking_minutes` — Represents and calculates an order line |
| `OrderStatus` | Order status values | Enum for order lifecycle stages |
| `Payment` | `bill`, `method`, `tendered`, `change`, `paid_at`, completion state | `process` — Processes a payment |
| `PaymentMethod` | Payment method values | Enum for supported payment methods |
| `PromoCode` | `code`, `discount`, validity dates, usage limits | `is_valid_on`, `remaining_uses`, `redeem` — Validates and redeems promo codes |
| `Tip` | `amount`, `waiter`, delivery state | `from_percent`, `percent_of`, `deliver` — Calculates and records a tip |

### `staff` — Employees, roles, shifts and payroll

| Class | Main data | Key behaviours |
|---|---|---|
| `ApprovalLimits` | `max_discount_percent`, `max_overtime_hours`, `refund_limit` | Stores manager approval limits |
| `Bartender` | `drinks_made`, alcohol certification | `can_serve_alcohol_to`, `serve_drink` — Checks age restrictions and serves drinks |
| `Cashier` | `register_number`, `cash_in_till`, `transactions_count` | `accept_cash`, `give_change`, `close_till` — Handles cash operations |
| `Chef` | `cuisine`, approved dishes | `approve`, `revoke`, `has_approved`, `suggest_special` — Approves dishes and suggests specials |
| `Cook` | `skill_level`, `station` | `can_work_station`, `move_to_station`, `promote`, `speed_factor`, `adjusted_minutes` — Checks skills and preparation speed |
| `Employee` | `hire_date`, `hourly_rate`, `is_active` | `years_of_service`, `give_raise`, `dismiss`, `reinstate`, `ensure_active` — Manages employee status and pay rate |
| `Manager` | `limits`, `approvals_count` | `can_approve_discount`, `can_approve_refund`, `approve_overtime`, `assign_shift` — Manages approvals and shifts |
| `Payroll` | `schedule`, tax and overtime settings, night bonus | `overtime_hours`, `night_bonus`, `gross_pay`, `payslip` — Calculates employee pay |
| `Schedule` | Shifts | `add_shift`, `remove_shift`, `shifts_on`, `shifts_of`, `on_duty_at`, `week_shifts`, `weekly_hours` — Manages employee schedules |
| `Shift` | `employee`, `day`, `start`, `end` | `duration_hours`, `overlaps`, `covers`, `night_hours` — Calculates and checks shifts |
| `Waiter` | `languages`, `guests_served`, `tips_total` | `speaks`, `receive_tip`, `serve_guests`, `average_tip_per_guest` — Tracks waiter service and tips |

### Root-level application and shared entities

| Class | Main data | Key behaviours |
|---|---|---|
| `Person` | `name`, `phone`, `birth_date` | `age_on`, `is_adult`, `matches` — Provides shared person data and age checks |
| `RestaurantApp` | Menu, inventory, staff, kitchen, orders, reservations, payments, reviews and deliveries | `run` — Runs the console menu and dispatches user actions |

---

## Custom exceptions

The project defines **15 custom exception classes**. They provide domain-specific error messages in Russian.

| Exception | Purpose |
|---|---|
| `RestaurantError` | Base exception for restaurant-domain errors |
| `InvalidDataError` | Invalid or corrupted input data |
| `InsufficientStockError` | Not enough ingredient stock to perform an operation |
| `DishUnavailableError` | A dish cannot currently be ordered or prepared |
| `AllergenConflictError` | A dish contains an allergen forbidden by the guest profile |
| `EmployeeNotAvailableError` | An employee is unavailable for the requested operation |
| `InsufficientPointsError` | Not enough loyalty points for redemption |
| `UnderageGuestError` | A guest is under the required age for an alcoholic drink |
| `TableUnavailableError` | A table or another hall resource is unavailable |
| `ReservationConflictError` | A table already has a reservation for the requested time |
| `OrderNotFoundError` | The requested order does not exist |
| `InvalidOrderStateError` | An operation is not allowed in the current order state |
| `PaymentDeclinedError` | A payment cannot be completed |
| `InvalidPromoCodeError` | A promo code is invalid, expired or unavailable |
| `KitchenOverloadError` | A kitchen station cannot accept more work |

---

## Console interface

Run the application from the `lab3` directory:

```bash
python -m restaurant
```

The interface and user-facing messages are in Russian. The console menu provides the following actions:

1. Show the restaurant menu.
2. Show currently available dishes.
3. View inventory balances.
4. Create an order.
5. View orders.
6. Get dish recommendations.
7. View dynamic prices.
8. Manage order preparation and serving.
9. Pay for an order.
10. Create a reservation.
11. Manage dish reviews.
12. View the sales report.
13. Manage delivery.
14. View the stop list.
15. Manage reservations.
16. Add a dish.
17. Change a dish price.
18. Delete a dish.
0. Exit.

The demo application starts with 15 dishes in four categories: salads, soups, main courses and desserts.

---

## Inventory persistence

Inventory batches are saved automatically in a JSON file. The file is created on the first application run and updated when stock changes and when the application exits.

The file is stored in the current user's application-data directory:

- Linux: `~/.local/share/RestaurantApp/inventory.json`
- Windows: `%LOCALAPPDATA%\RestaurantApp\inventory.json`
- macOS: `~/Library/Application Support/RestaurantApp/inventory.json`

On Linux, the application respects the `XDG_DATA_HOME` environment variable when it is set.

The JSON stores the ingredient name, batch quantity and original receipt date. This preserves expiry-date calculations between application launches. The JSON file is user data and should not be included in the source archive or GitHub Release assets.

---

## Development setup

All commands are run from the `lab3` directory.

### Create the environment and install development dependencies

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

### Run the console application

```bash
python -m restaurant
```

### Run unit tests and check coverage

```bash
python -m pytest
```

`pytest.ini` enables branch coverage and sets the minimum coverage threshold to 90%.

### Run the linter

```bash
python -m flake8 restaurant tests
```

The `.flake8` configuration sets a maximum line length of 150 characters and a maximum McCabe complexity of 6. It excludes virtual environments and generated cache directories.

---

## Project structure

```text
lab3/
├── restaurant/
│   ├── __init__.py
│   ├── __main__.py             # Application entry point and demo data
│   ├── app.py                  # Russian console interface
│   ├── exceptions.py           # 15 custom exceptions
│   ├── money.py                # Money-related value object
│   ├── person.py               # Shared person entity
│   ├── timeunits.py            # Time-related value object
│   ├── validation.py           # Shared validation helpers
│   ├── analytics/
│   │   ├── dynamic_pricer.py
│   │   ├── menu_recommender.py
│   │   ├── review.py
│   │   └── sales_report.py
│   ├── catalog/
│   │   ├── allergen.py
│   │   ├── ingredient.py
│   │   └── nutrition.py
│   ├── delivery/
│   │   ├── courier.py
│   │   └── delivery_order.py
│   ├── guests/
│   │   ├── customer.py
│   │   ├── loyalty.py
│   │   └── profile.py
│   ├── hall/
│   │   ├── banquet.py
│   │   ├── hall.py
│   │   ├── reservation.py
│   │   ├── reservation_book.py
│   │   ├── seating_planner.py
│   │   ├── table.py
│   │   └── waitlist.py
│   ├── inventory/
│   │   ├── inventory.py
│   │   ├── purchase_order.py
│   │   ├── stock_item.py
│   │   ├── storage.py
│   │   ├── supplier.py
│   │   └── waste_log.py
│   ├── kitchen/
│   │   ├── kitchen.py
│   │   ├── kitchen_station.py
│   │   └── kitchen_ticket.py
│   ├── menu/
│   │   ├── category.py
│   │   ├── dish.py
│   │   ├── menu.py
│   │   └── recipe.py
│   ├── orders/
│   │   ├── bill.py
│   │   ├── discount.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── payment.py
│   │   ├── promo_code.py
│   │   └── tip.py
│   └── staff/
│       ├── bartender.py
│       ├── cashier.py
│       ├── chef.py
│       ├── cook.py
│       ├── employee.py
│       ├── manager.py
│       ├── payroll.py
│       ├── schedule.py
│       ├── shift.py
│       └── waiter.py
├── tests/
│   ├── conftest.py
│   ├── constants.py
│   └── test_*.py
├── .flake8
├── pytest.ini
├── README.md
└── requirements-dev.txt
```

---

## Technical notes

- Python 3.10 or newer is required.
- The application uses the Python standard library at runtime.
- Development dependencies are `pytest`, `pytest-cov` and `flake8`.
- The domain model is separated into modules by responsibility.
- The console application depends on the `restaurant` domain package; domain classes do not depend on the console interface.
- Inventory persistence is limited to stock batches. Menu edits, orders and other in-memory application records are not persisted between runs.
- Branch coverage is measured by pytest-cov; a high percentage does not by itself prove that every business scenario has been tested.
