"""
In-memory data layer for the Inventory Management System.

For this lab we simulate a database using a plain Python list of
dictionaries (`_inventory`). Each item resembles a trimmed-down version
of the product data returned by the OpenFoodFacts API, plus the fields
a retail admin actually needs to manage stock (price, quantity, etc).

Example item shape:
{
    "id": 1,
    "product_name": "Organic Almond Milk",
    "brand": "Silk",
    "barcode": "0025293001473",
    "category": "Beverages",
    "price": 4.99,
    "stock": 20,
    "ingredients_text": "Filtered water, almonds, cane sugar, ...",
    "image_url": "https://...",
    "source": "manual" | "openfoodfacts"
}
"""

from itertools import count


class InventoryStore:
    """A tiny in-memory 'database' with auto-incrementing IDs.

    Wrapping the list + id counter in a class (rather than using bare
    module-level globals) makes it trivial to reset state between
    tests via `InventoryStore()` -- each instance starts fresh.
    """

    def __init__(self):
        self._items = []
        self._id_counter = count(1)
        self._seed()

    def _seed(self):
        """Pre-populate a couple of items so /inventory isn't empty
        on a fresh boot -- makes manual testing in Postman/CLI nicer."""
        self.create({
            "product_name": "Organic Almond Milk",
            "brand": "Silk",
            "barcode": "0025293001473",
            "category": "Beverages",
            "price": 4.99,
            "stock": 20,
            "ingredients_text": "Filtered water, almonds, cane sugar.",
            "image_url": "",
            "source": "manual",
        })
        self.create({
            "product_name": "Whole Wheat Bread",
            "brand": "Bakers Choice",
            "barcode": "0987654321000",
            "category": "Bakery",
            "price": 2.5,
            "stock": 35,
            "ingredients_text": "Whole wheat flour, water, yeast, salt.",
            "image_url": "",
            "source": "manual",
        })

    # -- CRUD helpers -----------------------------------------------

    def all(self):
        return self._items

    def get(self, item_id):
        return next((i for i in self._items if i["id"] == item_id), None)

    def create(self, data):
        item = {
            "id": next(self._id_counter),
            "product_name": data.get("product_name", "Unnamed product"),
            "brand": data.get("brand", ""),
            "barcode": data.get("barcode", ""),
            "category": data.get("category", ""),
            "price": float(data.get("price", 0) or 0),
            "stock": int(data.get("stock", 0) or 0),
            "ingredients_text": data.get("ingredients_text", ""),
            "image_url": data.get("image_url", ""),
            "source": data.get("source", "manual"),
        }
        self._items.append(item)
        return item

    def update(self, item_id, data):
        item = self.get(item_id)
        if item is None:
            return None
        # Only overwrite fields the caller actually sent (PATCH semantics)
        for field in ("product_name", "brand", "barcode", "category",
                      "ingredients_text", "image_url", "source"):
            if field in data:
                item[field] = data[field]
        if "price" in data:
            item["price"] = float(data["price"])
        if "stock" in data:
            item["stock"] = int(data["stock"])
        return item

    def delete(self, item_id):
        item = self.get(item_id)
        if item is None:
            return False
        self._items.remove(item)
        return True


# Single shared instance used by the Flask app during normal operation.
inventory_store = InventoryStore()
