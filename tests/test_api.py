from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Concurrent Order Fulfillment System"}


def test_get_producta():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_invalid_inventory_quantity():
    response = client.post("/inventory", params={
        "product_id": 2,
        "warehouse_id": 4,
        "quantity": -5
    })

    assert response.status_code == 422

def test_fulfill_already_processed_order():
    response = client.post("/orders/4/fulfill")

    assert response.status_code == 400