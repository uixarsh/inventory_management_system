from uuid import UUID

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate
from app.core.exceptions import NotFoundError, DuplicateEmailError


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    """Create a new customer. Raises DuplicateEmailError if email exists."""
    existing = db.query(Customer).filter(Customer.email == data.email).first()
    if existing:
        raise DuplicateEmailError(email=data.email)

    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: UUID) -> Customer:
    """Get a customer by ID. Raises NotFoundError if not found."""
    customer = (
        db.query(Customer).filter(Customer.customer_id == customer_id).first()
    )
    if not customer:
        raise NotFoundError(resource="Customer", resource_id=str(customer_id))
    return customer


def get_all_customers(db: Session) -> list[Customer]:
    """Return all customers."""
    return db.query(Customer).all()


def delete_customer(db: Session, customer_id: UUID) -> None:
    """Delete a customer by ID. Raises NotFoundError if not found."""
    customer = get_customer(db, customer_id)
    db.delete(customer)
    db.commit()
