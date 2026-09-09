import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import uuid

BASE_URL = "http://127.0.0.1:8000"


def post_request(url, params):
    query = urllib.parse.urlencode(params)

    request = urllib.request.Request(
        f"{url}?{query}",
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def fulfill_order(order_id):
    request = urllib.request.Request(
        f"{BASE_URL}/orders/{order_id}/fulfill",
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def test_concurrent_fulfillment():
    # Create fresh test data
    product_status, product = post_request(
        f"{BASE_URL}/products",
        {
            "name": "Concurrency Test Product",
            "sku":  f"CONCURRENCY-TEST-{uuid.uuid4().hex[:8]}"
        }
    )

    assert product_status == 200

    product_id = product["id"]

    warehouse_status, warehouse = post_request(
        f"{BASE_URL}/warehouses",
        {
            "name": "Concurrency Test Warehouse",
            "location": "Test Location"
        }
    )

    assert warehouse_status == 200

    warehouse_id = warehouse["id"]

    inventory_status, _ = post_request(
        f"{BASE_URL}/inventory",
        {
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity": 10
        }
    )

    assert inventory_status == 200

    # Create two orders, each requesting 8 units.
    order_ids = []

    for customer in ["Concurrency Customer A", "Concurrency Customer B"]:
        status, order = post_request(
            f"{BASE_URL}/orders",
            {
                "customer_name": customer,
                "product_id": product_id,
                "quantity": 8
            }
        )

        assert status == 200
        order_ids.append(order["order_id"])

    # Fulfill both orders at the same time.
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(fulfill_order, order_ids))

    print("\nConcurrent fulfillment results:")
    for result in results:
        print(result)

    success_count = sum(status == 200 for status, _ in results)
    failure_count = sum(status == 400 for status, _ in results)

    assert success_count == 1
    assert failure_count == 1