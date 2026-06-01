from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.exceptions import NotFoundError, DuplicateSKUError


def create_product(db: Session, data: ProductCreate) -> Product:
    """Create a new product. Raises DuplicateSKUError if SKU exists."""
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise DuplicateSKUError(sku=data.sku)

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: UUID) -> Product:
    """Get a product by ID. Raises NotFoundError if not found."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise NotFoundError(resource="Product", resource_id=str(product_id))
    return product


def get_all_products(db: Session) -> list[Product]:
    """Return all products."""
    return db.query(Product).all()


def update_product(db: Session, product_id: UUID, data: ProductUpdate) -> Product:
    """Update a product. Raises NotFoundError or DuplicateSKUError."""
    product = get_product(db, product_id)

    update_data = data.model_dump(exclude_unset=True)

    # Check for SKU uniqueness if SKU is being changed
    if "sku" in update_data and update_data["sku"] != product.sku:
        existing = db.query(Product).filter(Product.sku == update_data["sku"]).first()
        if existing:
            raise DuplicateSKUError(sku=update_data["sku"])

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: UUID) -> None:
    """Delete a product by ID. Raises NotFoundError if not found."""
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
