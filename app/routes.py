"""
REST API routes for the Inventory Management System.
Core CRUD: GET/POST/PATCH/DELETE on /inventory
External API helpers: /inventory/lookup (preview) and /inventory/import (save)
"""

from flask import Blueprint, jsonify, request

from app.models import inventory_store
from app.external_api import fetch_product_by_barcode, fetch_product_by_name

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# -- Core CRUD --------------------------------------------------------

@inventory_bp.get("/inventory")
def get_all_items():
    return jsonify(inventory_store.all()), 200


@inventory_bp.get("/inventory/<int:item_id>")
def get_item(item_id):
    item = inventory_store.get(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item), 200


@inventory_bp.post("/inventory")
def create_item():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if not data.get("product_name"):
        return jsonify({"error": "'product_name' is required"}), 400

    item = inventory_store.create(data)
    return jsonify(item), 201


@inventory_bp.patch("/inventory/<int:item_id>")
def update_item(item_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    item = inventory_store.update(item_id, data)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item), 200


@inventory_bp.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    deleted = inventory_store.delete(item_id)
    if not deleted:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# -- External API helper routes ---------------------------------------

@inventory_bp.get("/inventory/lookup")
def lookup_external_product():
    """Query OpenFoodFacts without touching our inventory. Lets the
    admin preview a product before deciding to import it."""
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify(
            {"error": "Provide a 'barcode' or 'name' query parameter"}
        ), 400

    result = (fetch_product_by_barcode(barcode) if barcode
              else fetch_product_by_name(name))

    if result is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404
    return jsonify(result), 200


@inventory_bp.post("/inventory/import")
def import_external_product():
    """Query OpenFoodFacts and save the result directly as a new
    inventory item."""
    data = request.get_json(silent=True) or {}
    barcode = data.get("barcode")
    name = data.get("name")

    if not barcode and not name:
        return jsonify(
            {"error": "Provide 'barcode' or 'name' in the request body"}
        ), 400

    result = (fetch_product_by_barcode(barcode) if barcode
              else fetch_product_by_name(name))

    if result is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    # Allow the admin to set stock/price at import time
    if "price" in data:
        result["price"] = data["price"]
    if "stock" in data:
        result["stock"] = data["stock"]

    item = inventory_store.create(result)
    return jsonify(item), 201
