from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)
from datetime import datetime
from sqlalchemy import (Boolean,
    DateTime,
    ForeignKey,
    String)
from datetime import datetime, timezone
class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,)
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,)
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,)
    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    products: Mapped[list["Product"]] = relationship(
        back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    price: Mapped[int]
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,)
    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,)
    category: Mapped["Category | None"] = relationship(
        back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product")
    is_active: Mapped[bool] = mapped_column(default=True)
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(default="customer")
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        back_populates="orders"
    )
    total: Mapped[int]
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    quantity: Mapped[int]
    unit_price: Mapped[int]
    order: Mapped["Order"] = relationship(
        back_populates="items"
    )
    product: Mapped["Product"] = relationship(
    back_populates="order_items"
    )

class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )



