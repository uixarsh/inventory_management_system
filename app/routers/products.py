from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductRead
from app.services import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    return product_service.create_product(db, data)


@router.get("/", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    """List all products."""
    return product_service.get_all_products(db)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get a product by ID."""
    return product_service.get_product(db, product_id)


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: UUID, data: ProductUpdate, db: Session = Depends(get_db)
):
    """Update a product."""
    return product_service.update_product(db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    """Delete a product."""
    product_service.delete_product(db, product_id)
