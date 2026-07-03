"""
REST API routes for the Inventory Management System.

Route plan (CRUD stage)
------------------------
GET    /inventory                 -> list all items
GET    /inventory/<id>             -> fetch one item
POST   /inventory                  -> create an item manually
PATCH  /inventory/<id>              -> partially update an item
DELETE /inventory/<id>              -> remove an item

GET    /health                      -> simple liveness check
"""

from flask import Blueprint, jsonify, request

from app.models import inventory_store

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


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