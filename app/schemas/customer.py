from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""

    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone_number: str = Field(..., min_length=1, max_length=20)


class CustomerRead(BaseModel):
    """Schema for reading customer data."""

    model_config = ConfigDict(from_attributes=True)

    customer_id: UUID
    full_name: str
    email: str
    phone_number: str
    created_at: datetime
