# Concurrent Order Fulfillment & Inventory Allocation System

A backend system that allocates limited inventory across multiple warehouses while preventing over-allocation when multiple orders are fulfilled concurrently.

## Problem

In a multi-warehouse fulfillment system, multiple customer orders may request the same product at the same time.

A simple inventory check can create a race condition:

1. Order A checks inventory → 10 units available
2. Order B checks inventory → 10 units available
3. Both orders attempt to allocate 8 units
4. The system could incorrectly allocate 16 units from only 10 available

This project addresses that problem using database transactions and row-level locking.

## Key Features

- Product management
- Warehouse management
- Inventory management
- Customer order creation
- Multi-warehouse inventory allocation
- Concurrent order fulfillment
- Row-level database locking
- Transaction rollback when inventory is insufficient
- Prevention of processing an already fulfilled order
- Input validation
- Automated API testing
- Automated concurrency testing

## Technology Stack

- **Python 3.11**
- **FastAPI**
- **PostgreSQL**
- **SQLAlchemy**
- **Psycopg**
- **Pytest**
- **Uvicorn**
- **Git / GitHub**

## System Architecture

```text
Client
  |
  v
FastAPI REST API
  |
  v
Fulfillment Logic
  |
  +--------------------+
  |                    |
  v                    v
PostgreSQL         Transaction
Database           & Row Locking
  |
  +-- Products
  +-- Warehouses
  +-- Inventory
  +-- Orders
  +-- Order Items
  +-- Allocations