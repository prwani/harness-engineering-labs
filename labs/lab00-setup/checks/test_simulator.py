from common.store_sim.app import products, reset


def test_seed_contains_known_catalog_issues():
    reset()
    assert any(product["price"] == 9999.00 for product in products)
    assert any("Ignore prior instructions" in product["description"] for product in products)
