import pytest

from app import create_app
from app import models as models_module


@pytest.fixture
def client():
    """Fresh Flask test client with a clean in-memory store per test.

    Rebuilding `inventory_store` before each test prevents state from
    one test (e.g. an item created in test_post) from leaking into
    another (e.g. test_get_all expecting exactly the seeded 2 items).
    """
    models_module.inventory_store = models_module.InventoryStore()

    import app.routes as routes_module
    routes_module.inventory_store = models_module.inventory_store

    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as test_client:
        yield test_client
