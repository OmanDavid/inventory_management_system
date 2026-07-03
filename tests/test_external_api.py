"""
Unit tests for app/external_api.py using unittest.mock to simulate
OpenFoodFacts responses, and for the /inventory/lookup and
/inventory/import routes that depend on it.
"""

from unittest.mock import patch, MagicMock

from app.external_api import fetch_product_by_barcode, fetch_product_by_name


FAKE_BARCODE_RESPONSE = {
    "status": 1,
    "product": {
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "code": "0025293001473",
        "categories": "Beverages, Plant-based drinks",
        "ingredients_text": "Filtered water, almonds, cane sugar.",
        "image_url": "https://images.example.com/almond-milk.jpg",
    },
}

FAKE_NOT_FOUND_RESPONSE = {"status": 0}

FAKE_SEARCH_RESPONSE = {
    "products": [
        {
            "product_name": "Whole Wheat Bread",
            "brands": "Bakers Choice",
            "code": "0987654321000",
            "categories": "Bakery",
            "ingredients_text": "Whole wheat flour, water, yeast, salt.",
            "image_url": "",
        }
    ]
}


def _mock_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.status_code = status_code
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


# -- fetch_product_by_barcode ------------------------------------------

@patch("app.external_api.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_get.return_value = _mock_response(FAKE_BARCODE_RESPONSE)

    result = fetch_product_by_barcode("0025293001473")

    assert result is not None
    assert result["product_name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    assert result["source"] == "openfoodfacts"
    mock_get.assert_called_once()


@patch("app.external_api.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = _mock_response(FAKE_NOT_FOUND_RESPONSE)

    result = fetch_product_by_barcode("0000000000000")

    assert result is None


@patch("app.external_api.requests.get")
def test_fetch_by_barcode_network_error_returns_none(mock_get):
    import requests
    mock_get.side_effect = requests.RequestException("network down")

    result = fetch_product_by_barcode("0025293001473")

    assert result is None


# -- fetch_product_by_name ---------------------------------------------

@patch("app.external_api.requests.get")
def test_fetch_by_name_success(mock_get):
    mock_get.return_value = _mock_response(FAKE_SEARCH_RESPONSE)

    result = fetch_product_by_name("whole wheat bread")

    assert result is not None
    assert result["product_name"] == "Whole Wheat Bread"
    mock_get.assert_called_once()


@patch("app.external_api.requests.get")
def test_fetch_by_name_no_results(mock_get):
    mock_get.return_value = _mock_response({"products": []})

    result = fetch_product_by_name("nonexistent product xyz")

    assert result is None


# -- Routes that depend on the external API -----------------------------

@patch("app.routes.fetch_product_by_barcode")
def test_lookup_route_success(mock_fetch, client):
    mock_fetch.return_value = {
        "product_name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "0025293001473",
        "category": "Beverages",
        "ingredients_text": "",
        "image_url": "",
        "price": 0,
        "stock": 0,
        "source": "openfoodfacts",
    }

    response = client.get("/inventory/lookup?barcode=0025293001473")

    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"


@patch("app.routes.fetch_product_by_barcode")
def test_lookup_route_not_found(mock_fetch, client):
    mock_fetch.return_value = None

    response = client.get("/inventory/lookup?barcode=0000000000000")

    assert response.status_code == 404


def test_lookup_route_requires_query_param(client):
    response = client.get("/inventory/lookup")
    assert response.status_code == 400


@patch("app.routes.fetch_product_by_name")
def test_import_route_creates_inventory_item(mock_fetch, client):
    mock_fetch.return_value = {
        "product_name": "Whole Wheat Bread",
        "brand": "Bakers Choice",
        "barcode": "0987654321000",
        "category": "Bakery",
        "ingredients_text": "",
        "image_url": "",
        "price": 0,
        "stock": 0,
        "source": "openfoodfacts",
    }

    response = client.post("/inventory/import",
                            json={"name": "whole wheat bread",
                                  "price": 3.0, "stock": 12})

    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Whole Wheat Bread"
    assert data["price"] == 3.0
    assert data["stock"] == 12
    assert data["source"] == "openfoodfacts"

    # Confirm it landed in the inventory list too
    all_items = client.get("/inventory").get_json()
    assert any(i["barcode"] == "0987654321000" for i in all_items)


@patch("app.routes.fetch_product_by_name")
def test_import_route_not_found(mock_fetch, client):
    mock_fetch.return_value = None

    response = client.post("/inventory/import", json={"name": "nonsense"})

    assert response.status_code == 404


def test_import_route_requires_barcode_or_name(client):
    response = client.post("/inventory/import", json={})
    assert response.status_code == 400
