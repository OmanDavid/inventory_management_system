"""
Unit tests for cli/cli.py.

The CLI is HTTP-driven (it calls the Flask API via `requests`), so
these tests mock `requests.get/post/patch/delete` rather than spinning
up a real server, and mock `builtins.input` to simulate user keystrokes.
"""

from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli import cli


def _mock_response(json_data, status_code=200):
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.status_code = status_code
    return mock_resp


@patch("cli.cli.requests.get")
def test_view_all_items_prints_items(mock_get, capsys):
    mock_get.return_value = _mock_response([
        {"id": 1, "product_name": "Almond Milk", "brand": "Silk",
         "price": 4.99, "stock": 20}
    ])

    cli.view_all_items()

    captured = capsys.readouterr()
    assert "Almond Milk" in captured.out
    mock_get.assert_called_once_with(f"{cli.BASE_URL}/inventory", timeout=5)


@patch("cli.cli.requests.get")
def test_view_all_items_handles_connection_error(mock_get, capsys):
    import requests
    mock_get.side_effect = requests.RequestException("connection refused")

    cli.view_all_items()

    captured = capsys.readouterr()
    assert "Could not reach the API" in captured.out


@patch("cli.cli.requests.get")
@patch("builtins.input", side_effect=["1"])
def test_view_single_item_success(mock_input, mock_get, capsys):
    mock_get.return_value = _mock_response(
        {"id": 1, "product_name": "Almond Milk", "brand": "Silk",
         "price": 4.99, "stock": 20, "barcode": "123",
         "category": "Beverages", "ingredients_text": "water, almonds"}
    )

    cli.view_single_item()

    captured = capsys.readouterr()
    assert "Almond Milk" in captured.out


@patch("builtins.input", side_effect=["abc"])
def test_view_single_item_rejects_non_numeric_id(mock_input, capsys):
    cli.view_single_item()
    captured = capsys.readouterr()
    assert "numeric ID" in captured.out


@patch("cli.cli.requests.post")
@patch("builtins.input", side_effect=["Peanut Butter", "Skippy", "", "5.25", "10"])
def test_add_item_success(mock_input, mock_post, capsys):
    mock_post.return_value = _mock_response(
        {"id": 3, "product_name": "Peanut Butter", "brand": "Skippy",
         "price": 5.25, "stock": 10}, status_code=201
    )

    cli.add_item()

    captured = capsys.readouterr()
    assert "Created" in captured.out
    assert "Peanut Butter" in captured.out


@patch("builtins.input", side_effect=[""])
def test_add_item_requires_product_name(mock_input, capsys):
    cli.add_item()
    captured = capsys.readouterr()
    assert "required" in captured.out


@patch("cli.cli.requests.patch")
@patch("builtins.input", side_effect=["1", "6.75", "5", ""])
def test_update_item_success(mock_input, mock_patch, capsys):
    mock_patch.return_value = _mock_response(
        {"id": 1, "product_name": "Almond Milk", "brand": "Silk",
         "price": 6.75, "stock": 5}
    )

    cli.update_item()

    captured = capsys.readouterr()
    assert "Updated" in captured.out


@patch("cli.cli.requests.delete")
@patch("builtins.input", side_effect=["2"])
def test_delete_item_success(mock_input, mock_delete, capsys):
    mock_delete.return_value = _mock_response(
        {"message": "Item 2 deleted"}
    )

    cli.delete_item()

    captured = capsys.readouterr()
    assert "deleted" in captured.out


@patch("cli.cli.requests.get")
@patch("builtins.input", side_effect=["0025293001473"])
def test_lookup_external_success(mock_input, mock_get, capsys):
    mock_get.return_value = _mock_response(
        {"product_name": "Organic Almond Milk", "brand": "Silk",
         "category": "Beverages"}
    )

    cli.lookup_external()

    captured = capsys.readouterr()
    assert "Organic Almond Milk" in captured.out


@patch("cli.cli.requests.post")
@patch("builtins.input", side_effect=["", "whole wheat bread", "3.0", "12"])
def test_import_external_success(mock_input, mock_post, capsys):
    mock_post.return_value = _mock_response(
        {"id": 5, "product_name": "Whole Wheat Bread", "brand": "Bakers",
         "price": 3.0, "stock": 12}, status_code=201
    )

    cli.import_external()

    captured = capsys.readouterr()
    assert "Imported" in captured.out
