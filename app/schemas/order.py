from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.customer import CustomerRead


class OrderItemCreate(BaseModel):
    """Schema for creating an order item (input)."""

    product_id: UUID
    quantity: int = Field(..., gt=0)


class OrderItemRead(BaseModel):
    """Schema for reading an order item (output)."""

    model_config = ConfigDict(from_attributes=True)

    order_item_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal


class OrderCreate(BaseModel):
    """Schema for creating a new order."""

    customer_id: UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderRead(BaseModel):
    """Schema for reading order data with nested customer and items."""

    model_config = ConfigDict(from_attributes=True)

    order_id: UUID
    customer_id: UUID
    total_amount: Decimal
    status: str
    created_at: datetime
    customer: CustomerRead
    items: list[OrderItemRead]
