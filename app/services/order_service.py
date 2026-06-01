from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.order import OrderCreate
from app.core.exceptions import NotFoundError, InsufficientStockError


def create_order(db: Session, data: OrderCreate) -> Order:
    """
    Create a new order with atomic stock validation and deduction.

    Business rules enforced:
    - Customer must exist
    - Every product in the order must exist
    - Each product must have sufficient stock
    - Stock check and deduction happen in the same transaction
    - If any product fails validation, the entire order is rejected
    - unit_price is snapshotted from product.price at creation time
    - total_amount = sum(item.quantity * item.unit_price)
    """
    # 1. Validate customer exists
    customer = (
        db.query(Customer).filter(Customer.customer_id == data.customer_id).first()
    )
    if not customer:
        raise NotFoundError(resource="Customer", resource_id=str(data.customer_id))

    # 2. Validate all products exist and have sufficient stock
    order_items_data = []
    for item in data.items:
        product = (
            db.query(Product).filter(Product.product_id == item.product_id).first()
        )
        if not product:
            raise NotFoundError(
                resource="Product", resource_id=str(item.product_id)
            )
        if product.quantity_in_stock < item.quantity:
            raise InsufficientStockError(
                sku=product.sku,
                requested=item.quantity,
                available=product.quantity_in_stock,
            )
        order_items_data.append((product, item.quantity))

    # 3. Create Order record
    order = Order(customer_id=data.customer_id, total_amount=Decimal("0"))
    db.add(order)
    db.flush()  # Get order_id without committing

    # 4. Create OrderItems and deduct stock
    total = Decimal("0")
    for product, quantity in order_items_data:
        unit_price = product.price  # Snapshot current price
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=product.product_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        db.add(order_item)

        # Deduct stock
        product.quantity_in_stock -= quantity

        total += Decimal(str(unit_price)) * quantity

    # 5. Set calculated total
    order.total_amount = total

    # 6. Commit entire transaction atomically
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: UUID) -> Order:
    """Get an order by ID with eager-loaded customer and items."""
    order = (
        db.query(Order)
        .options(joinedload(Order.customer), joinedload(Order.items))
        .filter(Order.order_id == order_id)
        .first()
    )
    if not order:
        raise NotFoundError(resource="Order", resource_id=str(order_id))
    return order


def get_all_orders(db: Session) -> list[Order]:
    return (
        db.query(Order)
        .options(
            joinedload(Order.customer),
            joinedload(Order.items)
        )
        .all()
    )


def delete_order(db: Session, order_id: UUID) -> None:
    """Delete/cancel an order by ID. Raises NotFoundError if not found."""
    order = (
        db.query(Order).filter(Order.order_id == order_id).first()
    )
    if not order:
        raise NotFoundError(resource="Order", resource_id=str(order_id))
    db.delete(order)
    db.commit()
