from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.order import OrderCreate, OrderRead
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    return order_service.create_order(db, data)


@router.get("/", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    """List all orders."""
    return order_service.get_all_orders(db)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    """Get an order by ID."""
    return order_service.get_order(db, order_id)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: UUID, db: Session = Depends(get_db)):
    """Cancel/delete an order."""
    order_service.delete_order(db, order_id)
