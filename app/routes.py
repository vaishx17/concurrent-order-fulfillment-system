from fastapi import APIRouter, Depends, HTTPException
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dependencies import get_db
from app.models import OrderItem, Product
from app.models import (
    Product,
    Warehouse,
    Inventory,
    Order,
    OrderItem,
    Allocation
)


router=APIRouter()

@router.post("/products")
def create_product(
    name: str,
    sku: str,
    db: Session = Depends(get_db)
):

    product = Product(name=name, sku=sku)

    db.add(product)
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku
    }

@router.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    
    return [
        {
            "id": product.id,
            "name": product.name,
            "sku": product.sku
        }
        for product in products
    ]

@router.post("/warehouses")
def create_warehouse(
    name: str,
    location: str,
    db: Session = Depends(get_db)
):
    warehouse = Warehouse(name=name, location=location)

    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)

    return {
        "id": warehouse.id,
        "name": warehouse.name,
        "location": warehouse.location
    }

@router.get("/warehouses")
def get_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).all()
    
    return [
        {
            "id": warehouse.id,
            "name": warehouse.name,
            "location": warehouse.location
        }
        for warehouse in warehouses
    ]

@router.post("/inventory")
def add_inventory(
    product_id: int,
    warehouse_id: int,
    quantity: int = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    inventory = Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity=quantity)

    db.add(inventory)
    db.commit()
    db.refresh(inventory)

    return {
        "id": inventory.id,
        "product_id": inventory.product_id,
        "warehouse_id": inventory.warehouse_id,
        "quantity": inventory.quantity
    }

@router.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    inventory = db.query(Inventory).all()

    return [
        {
            "id": item.id,
            "product_id": item.product_id,
            "warehouse_id": item.warehouse_id,
            "quantity": item.quantity
        }
        for item in inventory
    ]

@router.post("/orders")
def create_order(
    customer_name: str,
    product_id: int,
    quantity: int = Query(..., gt=0),
    db: Session = Depends(get_db)
):

    order = Order(customer_name=customer_name)
    
    db.add(order)
    db.flush()
    order_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity)
    
    db.add(order_item)
    db.commit()
    db.refresh(order)

    return{
        "order_id": order.id,
        "customer_name": order.customer_name,
        "status": order.status,
        "product_id": product_id,
        "quantity": quantity
    }


@router.post("/orders/{order_id}/fulfill")
def fulfill_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Order has already been processed"
        )

    order_item = db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).first()

    if not order_item:
        raise HTTPException(
            status_code=404,
            detail="Order item not found"
        )

    inventory_rows = db.query(Inventory).filter(
        Inventory.product_id == order_item.product_id,
        Inventory.quantity > 0
    ).order_by(Inventory.id).with_for_update().all()

    remaining = order_item.quantity
    allocations = []

    for inventory in inventory_rows:
        if remaining <= 0:
            break

        allocated_quantity = min(
            inventory.quantity,
            remaining
        )

        inventory.quantity -= allocated_quantity

        allocation = Allocation(
            order_item_id=order_item.id,
            warehouse_id=inventory.warehouse_id,
            quantity=allocated_quantity
        )

        db.add(allocation)

        allocations.append({
            "warehouse_id": inventory.warehouse_id,
            "quantity": allocated_quantity
        })

        remaining -= allocated_quantity

    if remaining > 0:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Insufficient inventory"
        )

    order.status = "fulfilled"

    db.commit()

    return {
        "order_id": order.id,
        "status": order.status,
        "allocations": allocations
    }