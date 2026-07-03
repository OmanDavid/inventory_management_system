# Inventory Management System

A Flask REST API for managing retail inventory, enriched with real-time
product data pulled from the [OpenFoodFacts API](https://openfoodfacts.github.io/openfoodfacts-server/api/).
Includes a CLI admin client and a pytest test suite.

## Features

- Full CRUD REST API for inventory items (`GET`, `POST`, `PATCH`, `DELETE`)
- External API integration: look up products by **barcode** or **name**
  on OpenFoodFacts, preview them, or import them straight into inventory
- CLI tool that drives the API exactly like a real admin frontend would
- In-memory "database" (a Python list) that seeds two sample items on boot
- pytest suite covering routes, external API calls (mocked), and CLI commands

## Project Structure

```
inventory_management_system/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # In-memory InventoryStore (simulated DB)
│   ├── routes.py         # Blueprint: all REST + helper routes
│   └── external_api.py   # OpenFoodFacts integration
├── cli/
│   └── cli.py             # CLI admin client (talks to the API over HTTP)
├── tests/
│   ├── conftest.py
│   ├── test_routes.py
│   ├── test_external_api.py
│   └── test_cli.py
├── run.py                 # Entry point for the Flask dev server
├── requirements.txt
├── pytest.ini
└── README.md
```

## Installation & Setup

1. Clone the repo and enter it:
   ```bash
   git clone https://github.com/OmanDavid/inventory-management-system.git
   cd inventory-management-system
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate     # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask server:
   ```bash
   python run.py
   ```
   The API will be live at `http://127.0.0.1:5000`.

5. In a **second terminal** (with the venv activated), run the CLI:
   ```bash
   python cli/cli.py
   ```

## API Endpoints

| Method | Route                | Description                                   |
|--------|-----------------------|------------------------------------------------|
| GET    | `/health`             | Liveness check                                 |
| GET    | `/inventory`          | List all inventory items                       |
| GET    | `/inventory/<id>`     | Fetch a single item                            |
| POST   | `/inventory`          | Create a new item manually                     |
| PATCH  | `/inventory/<id>`     | Partially update an item (price, stock, etc.)  |
| DELETE | `/inventory/<id>`     | Remove an item                                 |
| GET    | `/inventory/lookup`   | Preview a product from OpenFoodFacts (no save) |
| POST   | `/inventory/import`   | Fetch from OpenFoodFacts and save to inventory |

### Item shape

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "0025293001473",
  "category": "Beverages",
  "price": 4.99,
  "stock": 20,
  "ingredients_text": "Filtered water, almonds, cane sugar.",
  "image_url": "",
  "source": "manual"
}
```

### Example requests

**Create an item**
```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Peanut Butter", "brand": "Skippy", "price": 5.25, "stock": 10}'
```

**Update stock**
```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 15}'
```

**Preview a product from OpenFoodFacts by barcode**
```bash
curl "http://127.0.0.1:5000/inventory/lookup?barcode=0025293001473"
```

**Import a product from OpenFoodFacts by name, setting price/stock**
```bash
curl -X POST http://127.0.0.1:5000/inventory/import \
  -H "Content-Type: application/json" \
  -d '{"name": "whole wheat bread", "price": 3.00, "stock": 12}'
```

## CLI Usage

With the Flask server running, launch the CLI:

```bash
python cli/cli.py
```

You'll see a menu:

```
====== Inventory Management CLI ======
1. View all items
2. View a single item
3. Add a new item manually
4. Update an item (price/stock/name)
5. Delete an item
6. Look up a product on OpenFoodFacts (preview only)
7. Import a product from OpenFoodFacts into inventory
0. Exit
========================================
```

Each option prompts for the needed inputs and prints the API's response.
Invalid input (non-numeric IDs, unreachable server, product not found,
etc.) is handled gracefully with a clear message rather than crashing.

## Running Tests

```bash
pytest
```

or, for verbose output:

```bash
pytest -v
```

The suite (32 tests) covers:
- **Routes**: every CRUD endpoint, both success and error paths
- **External API**: `fetch_product_by_barcode` / `fetch_product_by_name`,
  mocked with `unittest.mock` so tests don't depend on network access
- **CLI**: each menu action, with `requests` and `input()` mocked

## Git Workflow

This project was developed using feature branches merged via pull
requests, for example:

- `feature/crud-routes` — core CRUD endpoints
- `feature/external-api` — OpenFoodFacts integration
- `feature/cli` — CLI client
- `feature/tests` — pytest suite

Each feature branch was merged into `main` via a pull request and
deleted after merge to keep the branch list clean.

## Notes on Design Decisions

- The "database" is an in-memory Python list (`InventoryStore` in
  `app/models.py`), per the lab's requirement to simulate storage with
  an array. It resets whenever the server restarts.
- `PATCH` (not `PUT`) is used for updates since admins typically only
  change one or two fields at a time (e.g. stock after a delivery).
- The external API integration is split into two routes: `/lookup`
  (read-only preview) and `/import` (fetch + persist), so an admin can
  check a product before deciding whether to add it to inventory.
- OpenFoodFacts does not provide pricing, so imported items default to
  `price: 0, stock: 0` unless the admin supplies them at import time.
