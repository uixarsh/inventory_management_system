from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    quantity_in_stock: int = Field(..., ge=0)


class ProductUpdate(BaseModel):
    """Schema for updating an existing product. All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = Field(None, min_length=1, max_length=100)
    price: Decimal | None = Field(None, ge=0, decimal_places=2)
    quantity_in_stock: int | None = Field(None, ge=0)


class ProductRead(BaseModel):
    """Schema for reading product data."""

    model_config = ConfigDict(from_attributes=True)

    product_id: UUID
    name: str
    sku: str
    price: Decimal
    quantity_in_stock: int
    created_at: datetime
    updated_at: datetime
