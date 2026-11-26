# Restaurant Management System

A Python object-oriented project that models the work of a restaurant. The project contains a Russian-language console application and a domain model covering the menu, recipes, ingredients, inventory, guests, employees, orders, kitchen operations, reservations, billing, payments, delivery and sales analytics.

The application is organised as the `restaurant` Python package. Runtime functionality uses the Python standard library. Inventory batches are persisted in a JSON file; the remaining application data is kept in memory while the program is running.

---

## Project metrics

The current project structure contains the following object-oriented design metrics used for the lab assignment:

| Metric | Count | Required minimum |
|---|---:|---:|
| Domain and application classes | **56** | 50 |
| Custom exception classes | **14** | — |
| All classes, including custom exceptions | **70** | 50 |
| Fields in domain and application classes | **203** | 150 |
| Public behaviour methods | **252** | 100 |
| Class associations | **110** | 30 |

Counting conventions:

- The 56 domain and application classes include model classes, enums, helper types and `RestaurantApp`; the 14 custom exception classes are counted separately.
- Fields are distinct instance attributes assigned to `self` or declared as dataclass fields in the 56 domain and application classes. Fields belonging to custom exception classes, enum constants and class-level role labels are not counted.
- Behaviour methods are public methods that implement domain logic. Constructors, private methods and property accessors are not counted as behaviours.
- An association is a distinct class-to-class relationship represented by a typed field or a typed method parameter. A class pair is counted once even if it appears in several methods.

---

## Main capabilities

### Menu and dishes

- Store dishes grouped into menu categories.
- Describe dishes with recipes, preparation steps, cooking time and ingredient requirements.
- Add, edit and delete dishes through the console.
- Check dish availability against current ingredient stock.
- Build and display a stop list for dishes whose ingredients are insufficient.
- Calculate the nutritional value of a dish and identify its allergens.

### Orders, bills and payments

- Create an order containing multiple dishes and specify the quantity of each dish.
- Add order items, change quantities and remove items while the order is in the appropriate state.
- Track the order lifecycle: new, in progress, ready, served, paid or cancelled.
- Send order items to kitchen stations and track preparation tickets.
- Calculate bills, discounts and promotional discounts, add tips and produce receipt lines.
- Process payments by cash or bank card; cash payments calculate change.
- Calculate the nutritional value and combined allergens of an entire order.
- Check a guest's forbidden allergens when a dish is added to an order.

### Inventory and suppliers

- Track ingredient stock in separate batches with receipt and expiry dates.
- Consume ingredients using the earliest-expiry-first approach.
- Check stock availability and calculate ingredient shortages.
- Identify expired and soon-to-expire stock batches.
- Replenish stock through the console.
- Store supplier price lists and calculate purchase-order costs and expected delivery dates.
- Save and restore inventory batches in JSON format.
- Record food waste with a reason and calculate waste summaries.

### Guests and recommendations

- Store customer information and dietary preferences.
- Track forbidden allergens, vegetarian preferences and maximum dish price in a guest profile.
- Check whether a dish is suitable for a guest.
- Keep order history by dish and calculate frequently ordered dishes.
- Recommend dishes from the current menu, exclude stopped dishes and, when inventory is provided, filter out dishes that cannot currently be prepared. `GuestProfile` provides checks for allergens, vegetarian preferences and maximum dish price; `Order.add_item()` enforces the guest's forbidden-allergen list.

### Kitchen and staff

- Organise kitchen stations and assign cooks to stations.
- Estimate preparation time using station workload and cook speed.
- Create and complete kitchen tickets and identify late tickets.
- Model employee roles such as waiter, cashier, cook, chef, bartender, manager and courier.
- Create shifts and schedules, check overlaps and calculate working hours.
- Calculate overtime, night bonuses and employee payroll.

### Hall and reservations

- Model halls, tables and table capacity.
- Create, cancel and update reservations; check for time conflicts.
- Identify no-shows and release reservations when required.
- Manage a waiting list and estimate waiting time.
- Select suitable tables and suggest alternative reservation times.
- Calculate the table requirements and price of a banquet.

### Reviews, delivery and analytics

- Create dish reviews and approve or reject pending reviews in the domain model. The console automatically approves reviews submitted through its interface and displays approved reviews.
- Create delivery orders, assign couriers and track delivery status. The console workflow creates, assigns and completes a delivery in one action; the domain model supports the individual delivery states.
- Apply dynamic dish pricing based on time of day and ingredient expiry dates.
- Calculate order count, revenue, average check, popular dishes and revenue by day.

Some domain capabilities are represented by model classes and tested independently; they are not all exposed as separate actions in the console menu.

---

## Classes by module

The 56 domain and application classes are grouped into the following modules. Enums and helper model types are included in these module totals.

| Module | Classes | Responsibility |
|---|---|---|
| `analytics` | `DynamicPricer`, `MenuRecommender`, `Review`, `ReviewStatus`, `SalesReport` | Dynamic prices, dish recommendations, review moderation and sales statistics |
| `catalog` | `Allergen`, `Ingredient`, `NutritionInfo` | Ingredient data, allergens and nutritional values |
| `delivery` | `Courier`, `DeliveryOrder`, `DeliveryStatus` | Courier assignments and delivery lifecycle |
| `guests` | `Customer`, `GuestProfile` | Customer details, preferences and order history |
| `hall` | `Banquet`, `Hall`, `Reservation`, `ReservationBook`, `SeatingPlanner`, `Table`, `Waitlist`, `WaitlistEntry` | Tables, reservations, seating, banquets and waiting lists |
| `inventory` | `Inventory`, `InventoryStorage`, `PurchaseOrder`, `StockItem`, `Supplier`, `WasteLog` | Stock batches, JSON storage, suppliers, purchases and waste records |
| `kitchen` | `Kitchen`, `KitchenStation`, `KitchenTicket` | Kitchen stations, workload and preparation tickets |
| `menu` | `Dish`, `Menu`, `MenuCategory`, `Recipe` | Menu structure, dishes and recipes |
| `orders` | `Bill`, `Discount`, `Order`, `OrderItem`, `OrderStatus`, `Payment`, `PaymentMethod`, `PromoCode`, `Tip` | Order lifecycle, billing, discounts, payments and tips |
| `staff` | `ApprovalLimits`, `Bartender`, `Cashier`, `Chef`, `Cook`, `Employee`, `Manager`, `Payroll`, `Schedule`, `Shift`, `Waiter` | Employee roles, schedules, shifts and payroll |
| Root package | `Person`, `RestaurantApp` | Shared person data and the console application |

Additional root-level modules provide shared functionality:

- `money.py` — decimal percentage calculations for monetary amounts.
- `timeunits.py` — time conversion constants.
- `validation.py` — common validation functions.
- `exceptions.py` — the custom exception hierarchy.
- `__main__.py` — demo data creation, inventory storage setup and application entry point.

---

## Custom exceptions

The project defines **14 custom exception classes**, including the base `RestaurantError` class. They represent errors specific to restaurant operations and provide Russian-language messages.

| Exception | Purpose |
|---|---|
| `RestaurantError` | Base exception for restaurant-domain errors |
| `InvalidDataError` | Invalid or corrupted input data |
| `InsufficientStockError` | Not enough ingredient stock to perform an operation |
| `DishUnavailableError` | A dish cannot currently be ordered or prepared |
| `AllergenConflictError` | A dish contains an allergen forbidden by the guest profile |
| `EmployeeNotAvailableError` | An employee is unavailable for the requested operation |
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

Run the application from the project root (`lab3`):

```bash
python -m restaurant
```

The console interface and user-facing messages are in Russian. The main menu provides the following actions:

| Option | Action |
|---:|---|
| 1 | Show the restaurant menu |
| 2 | Show currently available dishes |
| 3 | View inventory balances |
| 4 | Create an order containing one or more dishes |
| 5 | View orders |
| 6 | Get dish recommendations |
| 7 | View dynamic prices |
| 8 | Manage order preparation and serving |
| 9 | Pay for an order |
| 10 | Create a reservation |
| 11 | Submit a dish review or view approved reviews |
| 12 | View the sales report |
| 13 | Create and complete a delivery or view deliveries |
| 14 | View the stop list |
| 15 | Manage reservations |
| 16 | Add a dish |
| 17 | Change a dish price |
| 18 | Delete a dish |
| 19 | Replenish inventory |
| 20 | View nutritional information and allergens |
| 0 | Exit |

When creating an order, the user can select several dishes and set the quantity for each one. Entering `0` finishes dish selection. An order is not created when no dish has been selected.

The nutritional-information option has two actions:

1. Display the nutritional values per serving, allergens and vegetarian status of a dish.
2. Display the total nutritional values and combined allergens of an order.

The demo application starts with **15 dishes** in four categories: salads, soups, main courses and desserts. It also creates demo employees, an inventory and a kitchen station.

---

## Inventory persistence

Inventory batches are saved automatically in a JSON file. The file is written when stock batches are received, consumed or discarded, and again when the application exits. On startup, the application attempts to restore the saved batches.

The file is stored in the current user's application-data directory:

- Linux: `~/.local/share/RestaurantApp/inventory.json`
- Windows: `%LOCALAPPDATA%/RestaurantApp/inventory.json`
- macOS: `~/Library/Application Support/RestaurantApp/inventory.json`

On Linux, the application respects the `XDG_DATA_HOME` environment variable when it is set. On Windows, it uses `LOCALAPPDATA` when available.

The JSON file stores the ingredient name, batch quantity and original receipt date. Keeping the receipt date allows the application to calculate expiry dates after a restart. Inventory data is persisted; orders, reservations, payments, reviews, deliveries and menu changes are not saved between application runs.

The inventory JSON file is user data and should not be included in the source archive or Git repository.

---

## Development setup

All commands below are run from the `lab3` directory.

### Create a virtual environment and install development dependencies

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

Python **3.10 or newer** is required. The application itself uses only the Python standard library. Development dependencies are:

- `pytest` — test runner.
- `pytest-cov` — test coverage and branch coverage reports.
- `flake8` — code style and complexity checks.

### Run the console application

```bash
python -m restaurant
```

### Run tests and check coverage

```bash
python -m pytest
```

`pytest.ini` enables branch coverage and requires at least **90%** total coverage. The supplied project archive was checked with **289 passing tests** and **98.01%** total coverage.

### Run the linter

```bash
python -m flake8 restaurant tests
```

The `.flake8` configuration sets a maximum line length of **150 characters** and a maximum McCabe complexity of **6**. Virtual environments and generated cache directories are excluded. Run the linter against `restaurant` and `tests`, not against the entire project directory, so that installed packages in the virtual environment are not analysed.

---

## Project structure

```text
lab3/
├── README.md
├── requirements-dev.txt
├── pytest.ini
├── .flake8
├── restaurant/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py
│   ├── exceptions.py
│   ├── money.py
│   ├── person.py
│   ├── timeunits.py
│   ├── validation.py
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── dynamic_pricer.py
│   │   ├── menu_recommender.py
│   │   ├── review.py
│   │   └── sales_report.py
│   ├── catalog/
│   │   ├── __init__.py
│   │   ├── allergen.py
│   │   ├── ingredient.py
│   │   └── nutrition.py
│   ├── delivery/
│   │   ├── __init__.py
│   │   ├── courier.py
│   │   └── delivery_order.py
│   ├── guests/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   └── profile.py
│   ├── hall/
│   │   ├── __init__.py
│   │   ├── banquet.py
│   │   ├── hall.py
│   │   ├── reservation.py
│   │   ├── reservation_book.py
│   │   ├── seating_planner.py
│   │   ├── table.py
│   │   └── waitlist.py
│   ├── inventory/
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── purchase_order.py
│   │   ├── stock_item.py
│   │   ├── storage.py
│   │   ├── supplier.py
│   │   └── waste_log.py
│   ├── kitchen/
│   │   ├── __init__.py
│   │   ├── kitchen.py
│   │   ├── kitchen_station.py
│   │   └── kitchen_ticket.py
│   ├── menu/
│   │   ├── __init__.py
│   │   ├── category.py
│   │   ├── dish.py
│   │   ├── menu.py
│   │   └── recipe.py
│   ├── orders/
│   │   ├── __init__.py
│   │   ├── bill.py
│   │   ├── discount.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── payment.py
│   │   ├── promo_code.py
│   │   └── tip.py
│   └── staff/
│       ├── __init__.py
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
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── constants.py
    └── test_*.py
```

---

## Technical notes

- Python 3.10 or newer is required.
- The application uses the Python standard library at runtime.
- Development dependencies are listed in `requirements-dev.txt`.
- The domain model is organised into modules by responsibility.
- `RestaurantApp` coordinates the console interface and uses the domain package; domain classes do not depend on the console interface.
- Inventory persistence is limited to stock batches. Other application records are not persisted between runs.
- Test coverage is measured with branch coverage. A high coverage percentage does not by itself prove that every possible business scenario has been tested.
