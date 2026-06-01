# Inventory & Order Management System — Backend Build Plan

---

## 1. Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | FastAPI |
| ORM | SQLAlchemy (classic) |
| Database | PostgreSQL 16 |
| Validation | Pydantic v2 + pydantic-settings |
| Containerization | Docker + Docker Compose |
| Server | Uvicorn |

---

## 2. Folder Structure
inventory-system/
├── backend/
│   ├── app/
│   │   ├── init.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   │
│   │   ├── models/
│   │   │   ├── init.py
│   │   │   ├── product.py
│   │   │   ├── customer.py
│   │   │   ├── order.py
│   │   │   └── order_item.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── init.py
│   │   │   ├── product.py
│   │   │   ├── customer.py
│   │   │   └── order.py
│   │   │
│   │   ├── routers/
│   │   │   ├── init.py
│   │   │   ├── products.py
│   │   │   ├── customers.py
│   │   │   └── orders.py
│   │   │
│   │   ├── services/
│   │   │   ├── init.py
│   │   │   ├── product_service.py
│   │   │   ├── customer_service.py
│   │   │   └── order_service.py
│   │   │
│   │   └── core/
│   │       ├── init.py
│   │       ├── config.py
│   │       └── exceptions.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
│
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
└── README.md

---

## 3. Database Schema

### products
| Column | Type | Constraints |
|---|---|---|
| product_id | UUID | PK, default uuid4 |
| name | VARCHAR(255) | NOT NULL |
| sku | VARCHAR(100) | UNIQUE, NOT NULL |
| price | NUMERIC(10,2) | NOT NULL, >= 0 |
| quantity_in_stock | INTEGER | NOT NULL, >= 0 |
| created_at | TIMESTAMP | default now() |
| updated_at | TIMESTAMP | auto-updated |

### customers
| Column | Type | Constraints |
|---|---|---|
| customer_id | UUID | PK, default uuid4 |
| full_name | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| phone_number | VARCHAR(20) | NOT NULL |
| created_at | TIMESTAMP | default now() |

### orders
| Column | Type | Constraints |
|---|---|---|
| order_id | UUID | PK, default uuid4 |
| customer_id | UUID | FK → customers.customer_id |
| total_amount | NUMERIC(10,2) | calculated by backend |
| status | VARCHAR(50) | default "pending" |
| created_at | TIMESTAMP | default now() |

### order_items
| Column | Type | Constraints |
|---|---|---|
| order_item_id | UUID | PK, default uuid4 |
| order_id | UUID | FK → orders.order_id |
| product_id | UUID | FK → products.product_id |
| quantity | INTEGER | NOT NULL, > 0 |
| unit_price | NUMERIC(10,2) | snapshot at order time |

---

## 4. Relationships
Customer ──< Order ──< OrderItem >── Product

- One Customer → many Orders
- One Order → many OrderItems
- One Product → many OrderItems
- Orders and Products are linked through OrderItem (many-to-many)
- unit_price is snapshotted on OrderItem at creation time — never calculated
  from the live product price after the fact

---

## 5. API Endpoints

### Products
| Method | Endpoint | Description | Success Code |
|---|---|---|---|
| POST | /products | Create product | 201 |
| GET | /products | List all products | 200 |
| GET | /products/{id} | Get product by ID | 200 |
| PUT | /products/{id} | Update product | 200 |
| DELETE | /products/{id} | Delete product | 204 |

### Customers
| Method | Endpoint | Description | Success Code |
|---|---|---|---|
| POST | /customers | Create customer | 201 |
| GET | /customers | List all customers | 200 |
| GET | /customers/{id} | Get customer by ID | 200 |
| DELETE | /customers/{id} | Delete customer | 204 |

### Orders
| Method | Endpoint | Description | Success Code |
|---|---|---|---|
| POST | /orders | Create order | 201 |
| GET | /orders | List all orders | 200 |
| GET | /orders/{id} | Get order by ID | 200 |
| DELETE | /orders/{id} | Cancel/delete order | 204 |

---

## 6. Pydantic Schemas (per resource)

Each resource needs three schema variants:

### Product
- `ProductCreate` — name, sku, price, quantity_in_stock (all required)
- `ProductUpdate` — all fields optional (PATCH-style even on PUT)
- `ProductRead` — all fields including product_id, created_at, updated_at

### Customer
- `CustomerCreate` — full_name, email, phone_number
- `CustomerRead` — all fields including customer_id, created_at

### Order
- `OrderItemCreate` — product_id, quantity
- `OrderCreate` — customer_id, list of OrderItemCreate
- `OrderRead` — full order with nested customer and order items

---

## 7. Business Logic Rules

All of this lives in the services layer, never in routers.

### Product Rules
- SKU must be unique — check before insert, raise `DuplicateSKUError` if not
- Price cannot be negative — enforce at schema level (Pydantic ge=0)
- Quantity cannot be negative — enforce at schema level (Pydantic ge=0)

### Customer Rules
- Email must be unique — check before insert, raise `DuplicateEmailError` if not

### Order Rules
- Customer must exist before order is created
- Every product in the order must exist
- Each product must have sufficient stock before the order is committed
- Stock check and stock deduction must happen in the same DB transaction
- If any product is out of stock, the entire order is rejected — no partial orders
- total_amount is calculated as: sum(item.quantity * item.unit_price) for all items
- unit_price is copied from product.price at the moment the order is created

---

## 8. Services Layer Detail

### product_service.py
create_product(db, data) → Product
get_product(db, product_id) → Product
get_all_products(db) → list[Product]
update_product(db, product_id, data) → Product
delete_product(db, product_id) → None

### customer_service.py
create_customer(db, data) → Customer
get_customer(db, customer_id) → Customer
get_all_customers(db) → list[Customer]
delete_customer(db, customer_id) → None

### order_service.py
create_order(db, data) → Order

Validate customer exists
For each item: validate product exists, check stock
If any check fails: raise InsufficientStockError, abort entire order
Create Order record
For each item: create OrderItem, deduct stock from product
Calculate and set total_amount
Commit transaction
Return Order with items

get_order(db, order_id) → Order
get_all_orders(db) → list[Order]
delete_order(db, order_id) → None

---

## 9. Error Handling

### Custom Exceptions (core/exceptions.py)
```python
class NotFoundError(Exception): ...
class DuplicateSKUError(Exception): ...
class DuplicateEmailError(Exception): ...
class InsufficientStockError(Exception): ...
class InvalidQuantityError(Exception): ...
```

### HTTP Error Mapping
| Exception | HTTP Status | Message |
|---|---|---|
| NotFoundError | 404 | Resource not found |
| DuplicateSKUError | 409 | SKU already exists |
| DuplicateEmailError | 409 | Email already registered |
| InsufficientStockError | 422 | Insufficient stock for product {sku} |
| InvalidQuantityError | 422 | Quantity must be greater than 0 |
| Unhandled Exception | 500 | Internal server error |

Register all handlers in main.py using `@app.exception_handler`.

---

## 10. core/config.py

Use pydantic-settings to read all config from environment:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    APP_ENV: str = "development"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

---

## 11. database.py

```python
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

---

## 12. dependencies.py

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 13. Docker Setup

### backend/Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app

  db:
    image: postgres:16-alpine
    env_file:
      - .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### .env.example
DATABASE_URL=postgresql://user:password@db:5432/inventory_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=inventory_db
APP_ENV=development
DEBUG=False

### .dockerignore
pycache
*.pyc
*.pyo
.env
.git
.gitignore
*.md

---

## 14. requirements.txt
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
pydantic>=2.7.0
pydantic-settings>=2.2.0
python-dotenv>=1.0.0

---

## 15. .gitignore
Python
pycache/
*.py[cod]
*.pyo
*.pyd
.Python
env/
venv/
.venv/
Env
.env
Docker
*.log
IDE
.vscode/
.idea/
OS
.DS_Store
Thumbs.db

---

## 16. Build Order

Follow this exact sequence to avoid wasted debugging time:
Step 1 — core/config.py + database.py
Get DB connection working. Test with a raw engine.connect().
Step 2 — models/
Define all four models. Run Base.metadata.create_all()
and verify tables appear in Postgres.
Step 3 — schemas/
Write Create, Update, Read variants for all three resources.
Step 4 — dependencies.py
Wire up get_db(). Nothing else depends on this being perfect
but everything downstream needs it.
Step 5 — services/
Implement all service functions. Write them as plain Python,
no FastAPI imports. Test logic directly if needed.
Step 6 — routers/
Thin wrappers. Each route calls one service function,
returns a schema, handles nothing else.
Step 7 — core/exceptions.py + main.py
Register exception handlers. Mount all routers.
Step 8 — Dockerfile + docker-compose.yml
Containerize last once the app runs clean locally.
Step 9 — .env, .env.example, .gitignore, README.md

---

## 17. README.md Outline
Inventory & Order Management System
Overview
Tech Stack
Prerequisites (Docker, Docker Compose)
Getting Started

Clone repo
Copy .env.example to .env and fill values
docker compose up --build

API Docs

Available at http://localhost:8000/docs (Swagger UI)

Project Structure
Environment Variables

---

## Key Reminders

- Never put business logic in routers
- Always snapshot unit_price on OrderItem at order creation time
- Stock check and deduction must be atomic — single transaction
- Never hardcode credentials anywhere — everything through .env
- Use UUIDs as primary keys, not auto-increment integers