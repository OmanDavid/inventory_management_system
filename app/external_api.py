"""
Integration with the OpenFoodFacts public API.

Docs: https://openfoodfacts.github.io/openfoodfacts-server/api/

Two lookup strategies are supported, matching how a store employee would
actually search for a product:
  * by barcode (exact product lookup)
  * by product name (free-text search, returns the closest match)

Both functions return a normalized dict shaped like our internal
inventory items (see app/models.py) so the caller can drop the result
straight into the store, or `None` if nothing was found / the request
failed. Network/par. errors are caught so a flaky external API never
crashes the Flask app -- callers just get None back.
"""

import requests

BARCODE_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
TIMEOUT = 8  # seconds
HEADERS = {
    "User-Agent": "InventoryManagementSystem/1.0 (Moringa School lab; contact: oman@example.com)"
}


def _normalize(product):
    """Convert a raw OpenFoodFacts 'product' object into our schema."""
    return {
        "product_name": product.get("product_name") or "Unknown product",
        "brand": product.get("brands", ""),
        "barcode": product.get("code", "") or product.get("_id", ""),
        "category": (product.get("categories", "").split(",")[0]
                      if product.get("categories") else ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_url", ""),
        "price": 0,   # OpenFoodFacts doesn't provide pricing
        "stock": 0,   # left for the admin to set after import
        "source": "openfoodfacts",
    }


def fetch_product_by_barcode(barcode):
    """Look up a single product by barcode. Returns a normalized dict
    or None if not found / on error."""
    try:
        response = requests.get(
            BARCODE_URL.format(barcode=barcode), headers=HEADERS, timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    if data.get("status") != 1:
        return None

    return _normalize(data.get("product", {}))


def fetch_product_by_name(name):
    """Search for a product by free-text name. Returns a normalized
    dict for the first/best match, or None if nothing was found."""
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }
    try:
        response = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    products = data.get("products", [])
    if not products:
        return None

    return _normalize(products[0])
