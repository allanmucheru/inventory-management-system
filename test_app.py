import pytest
from app import app, inventory_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Reset database state before each test
        inventory_db.clear()
        inventory_db.append({
            "id": 1,
            "name": "Test Item",
            "barcode": "123456",
            "category": "Test",
            "quantity": 10,
            "price": 2.50
        })
        yield client

def test_get_inventory(client):
    res = client.get("/api/inventory")
    assert res.status_code == 200
    assert res.json["count"] == 1

def test_get_single_item(client):
    res = client.get("/api/inventory/1")
    assert res.status_code == 200
    assert res.json["data"]["name"] == "Test Item"

def test_get_single_item_not_found(client):
    res = client.get("/api/inventory/999")
    assert res.status_code == 404

def test_create_item(client):
    payload = {"name": "New Apples", "quantity": 50, "price": 0.99, "category": "Produce"}
    res = client.post("/api/inventory", json=payload)
    assert res.status_code == 201
    assert res.json["data"]["name"] == "New Apples"

def test_update_item_patch(client):
    payload = {"quantity": 15, "price": 3.00}
    res = client.patch("/api/inventory/1", json=payload)
    assert res.status_code == 200
    assert res.json["data"]["quantity"] == 15
    assert res.json["data"]["price"] == 3.00

def test_search_helper_route(client):
    res = client.get("/api/inventory/search?q=test")
    assert res.status_code == 200
    assert len(res.json["data"]) == 1

def test_delete_item(client):
    res = client.delete("/api/inventory/1")
    assert res.status_code == 200
    
    # Verify deletion
    res_get = client.get("/api/inventory/1")
    assert res_get.status_code == 404

def test_external_api_fetch(client, monkeypatch):
    # Mock external API response from OpenFoodFacts
    def mock_fetch(barcode):
        return {"name": "Mocked Cereal", "category": "Breakfast", "barcode": barcode}

    monkeypatch.setattr("app.fetch_openfoodfacts_product", mock_fetch)
    
    res = client.post("/api/inventory/fetch-external/999999", json={"quantity": 5, "price": 4.50})
    assert res.status_code == 201
    assert res.json["data"]["name"] == "Mocked Cereal"
