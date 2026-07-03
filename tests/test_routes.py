"""Unit tests for the Flask REST API routes (CRUD)."""


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_get_all_items_returns_seeded_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2  # two items seeded in InventoryStore._seed
    assert data[0]["product_name"] == "Organic Almond Milk"


def test_get_single_item_success(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_create_item_success(client):
    payload = {
        "product_name": "Peanut Butter",
        "brand": "Skippy",
        "price": 5.25,
        "stock": 10,
    }
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Peanut Butter"
    assert data["price"] == 5.25
    assert data["stock"] == 10
    assert "id" in data

    # Confirm it was actually persisted into the store
    follow_up = client.get(f"/inventory/{data['id']}")
    assert follow_up.status_code == 200


def test_create_item_missing_name_fails(client):
    response = client.post("/inventory", json={"brand": "No Name Brand"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_item_requires_json_body(client):
    response = client.post("/inventory", data="not json")
    assert response.status_code == 400


def test_patch_item_updates_price_and_stock(client):
    response = client.patch("/inventory/1", json={"price": 6.75, "stock": 5})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 6.75
    assert data["stock"] == 5
    # Untouched fields should remain the same
    assert data["product_name"] == "Organic Almond Milk"


def test_patch_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 1})
    assert response.status_code == 404


def test_delete_item_success(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200
    assert "deleted" in response.get_json()["message"]

    # Confirm it's actually gone
    follow_up = client.get("/inventory/2")
    assert follow_up.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404
