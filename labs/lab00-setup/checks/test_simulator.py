from fastapi.testclient import TestClient

from common.store_sim.app import app, products, reset


def test_seed_contains_known_catalog_issues():
    reset()
    assert any(product["price"] == 9999.00 for product in products)
    assert any("Ignore prior instructions" in product["description"] for product in products)


def test_product_http_surface_and_reset():
    client = TestClient(app)
    assert client.get("/product").status_code == 200
    assert client.get("/product/1").json()["name"] == "Collar"
    assert client.get("/product/missing").status_code == 404
    assert client.post("/reset").json()["status"] == "reset"
