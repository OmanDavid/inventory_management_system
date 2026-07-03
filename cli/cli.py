"""
Command-line interface for the Inventory Management System.

This CLI is a thin client: it never touches app/models.py directly, it
only talks to the Flask API over HTTP (exactly like a real admin
frontend would). Run the Flask server first (`python run.py`), then run
this in a separate terminal:

    python cli/cli.py

Menu options let the admin:
  1. View all inventory items
  2. View a single item
  3. Add a new item manually
  4. Update an item's price/stock (or any field)
  5. Delete an item
  6. Look up a product on OpenFoodFacts (preview only)
  7. Import a product from OpenFoodFacts straight into inventory
  0. Exit
"""

import requests

BASE_URL = "http://127.0.0.1:5000"


def _print_item(item):
    print(f"  [{item['id']}] {item['product_name']} "
          f"({item.get('brand', 'no brand')}) "
          f"- ${item['price']:.2f} | stock: {item['stock']}")


def _handle_response(response, success_codes=(200, 201)):
    """Shared response handling: prints errors from the API in a
    friendly way, returns the parsed JSON on success or None."""
    try:
        payload = response.json()
    except ValueError:
        print(f"  Unexpected response from server (status "
              f"{response.status_code}).")
        return None

    if response.status_code not in success_codes:
        print(f"  Error: {payload.get('error', 'Unknown error')}")
        return None
    return payload


def view_all_items():
    try:
        response = requests.get(f"{BASE_URL}/inventory", timeout=5)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    items = _handle_response(response)
    if not items:
        print("  No items in inventory." if items == [] else "")
        return
    print(f"\n  {len(items)} item(s) in inventory:")
    for item in items:
        _print_item(item)


def view_single_item():
    item_id = input("  Item ID: ").strip()
    if not item_id.isdigit():
        print("  Please enter a numeric ID.")
        return
    try:
        response = requests.get(f"{BASE_URL}/inventory/{item_id}", timeout=5)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    item = _handle_response(response)
    if item:
        _print_item(item)
        print(f"  Barcode: {item.get('barcode', 'n/a')}")
        print(f"  Category: {item.get('category', 'n/a')}")
        print(f"  Ingredients: {item.get('ingredients_text', 'n/a')}")


def add_item():
    print("  Enter new item details (leave blank to skip a field):")
    product_name = input("  Product name (required): ").strip()
    if not product_name:
        print("  Product name is required. Cancelled.")
        return

    payload = {"product_name": product_name}
    brand = input("  Brand: ").strip()
    if brand:
        payload["brand"] = brand
    barcode = input("  Barcode: ").strip()
    if barcode:
        payload["barcode"] = barcode
    price = input("  Price: ").strip()
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("  Invalid price, skipping.")
    stock = input("  Stock quantity: ").strip()
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("  Invalid stock number, skipping.")

    try:
        response = requests.post(f"{BASE_URL}/inventory", json=payload,
                                  timeout=5)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    item = _handle_response(response, success_codes=(201,))
    if item:
        print("  Created:")
        _print_item(item)


def update_item():
    item_id = input("  Item ID to update: ").strip()
    if not item_id.isdigit():
        print("  Please enter a numeric ID.")
        return

    print("  Leave a field blank to leave it unchanged.")
    payload = {}
    price = input("  New price: ").strip()
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("  Invalid price, skipping.")
    stock = input("  New stock quantity: ").strip()
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("  Invalid stock number, skipping.")
    name = input("  New product name: ").strip()
    if name:
        payload["product_name"] = name

    if not payload:
        print("  Nothing to update. Cancelled.")
        return

    try:
        response = requests.patch(f"{BASE_URL}/inventory/{item_id}",
                                   json=payload, timeout=5)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    item = _handle_response(response)
    if item:
        print("  Updated:")
        _print_item(item)


def delete_item():
    item_id = input("  Item ID to delete: ").strip()
    if not item_id.isdigit():
        print("  Please enter a numeric ID.")
        return
    try:
        response = requests.delete(f"{BASE_URL}/inventory/{item_id}",
                                    timeout=5)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    result = _handle_response(response)
    if result:
        print(f"  {result['message']}")


def lookup_external():
    print("  Search OpenFoodFacts by barcode or name.")
    barcode = input("  Barcode (leave blank to search by name instead): ").strip()
    params = {}
    if barcode:
        params["barcode"] = barcode
    else:
        name = input("  Product name: ").strip()
        if not name:
            print("  Nothing entered. Cancelled.")
            return
        params["name"] = name

    try:
        response = requests.get(f"{BASE_URL}/inventory/lookup",
                                 params=params, timeout=10)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    result = _handle_response(response)
    if result:
        print("  Found on OpenFoodFacts:")
        print(f"    Name: {result['product_name']}")
        print(f"    Brand: {result.get('brand', 'n/a')}")
        print(f"    Category: {result.get('category', 'n/a')}")


def import_external():
    print("  Import a product from OpenFoodFacts into inventory.")
    barcode = input("  Barcode (leave blank to search by name instead): ").strip()
    payload = {}
    if barcode:
        payload["barcode"] = barcode
    else:
        name = input("  Product name: ").strip()
        if not name:
            print("  Nothing entered. Cancelled.")
            return
        payload["name"] = name

    price = input("  Set a price for this item: ").strip()
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("  Invalid price, skipping.")
    stock = input("  Set stock quantity: ").strip()
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("  Invalid stock number, skipping.")

    try:
        response = requests.post(f"{BASE_URL}/inventory/import",
                                  json=payload, timeout=10)
    except requests.RequestException:
        print("  Could not reach the API. Is the Flask server running?")
        return
    item = _handle_response(response, success_codes=(201,))
    if item:
        print("  Imported into inventory:")
        _print_item(item)


MENU = """
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
"""

ACTIONS = {
    "1": view_all_items,
    "2": view_single_item,
    "3": add_item,
    "4": update_item,
    "5": delete_item,
    "6": lookup_external,
    "7": import_external,
}


def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("  Invalid option, try again.")
            continue
        action()


if __name__ == "__main__":
    main()
