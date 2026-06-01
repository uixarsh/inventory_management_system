# Inventory & Order Management System

## Overview
A backend API for managing product inventory, customers, and orders. Built with FastAPI, SQLAlchemy, and PostgreSQL.

## Tech Stack
- **Language:** Python 3.12
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL 16
- **Validation:** Pydantic v2
- **Containerization:** Docker + Docker Compose

## Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your desired values
   ```

3. **Start the application**
   ```bash
   docker compose up --build
   ```

4. **Access the API**
   - Base URL: `http://localhost:8000`
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Docs

Interactive API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI).

### Endpoints

#### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products` | Create a product |
| GET | `/products` | List all products |
| GET | `/products/{id}` | Get product by ID |
| PUT | `/products/{id}` | Update a product |
| DELETE | `/products/{id}` | Delete a product |

#### Customers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/customers` | Create a customer |
| GET | `/customers` | List all customers |
| GET | `/customers/{id}` | Get customer by ID |
| DELETE | `/customers/{id}` | Delete a customer |

#### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create an order |
| GET | `/orders` | List all orders |
| GET | `/orders/{id}` | Get order by ID |
| DELETE | `/orders/{id}` | Cancel/delete an order |

## Project Structure
```
backend/
├── app/
│   ├── main.py            # FastAPI app, exception handlers, router mounting
│   ├── database.py        # SQLAlchemy engine, session, Base
│   ├── dependencies.py    # FastAPI dependencies (get_db)
│   ├── core/
│   │   ├── config.py      # Settings from environment
│   │   └── exceptions.py  # Custom exception classes
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic layer
│   └── routers/           # API route handlers
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
└── README.md
```

## Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `POSTGRES_USER` | Database user | — |
| `POSTGRES_PASSWORD` | Database password | — |
| `POSTGRES_DB` | Database name | — |
| `APP_ENV` | Environment (development/production) | `development` |
| `DEBUG` | Enable debug mode | `False` |
