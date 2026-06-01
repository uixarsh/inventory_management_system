import uuid

from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.order_id"),
        nullable=False,
    )
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.product_id"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self) -> str:
        return (
            f"<OrderItem(order='{self.order_id}', "
            f"product='{self.product_id}', qty={self.quantity})>"
        )
