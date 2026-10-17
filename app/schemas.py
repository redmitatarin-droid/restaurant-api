from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)
from pydantic import EmailStr
from datetime import datetime

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    price: int = Field(gt=0)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )
    category_id: int | None = None

class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    price: int | None = Field(
        default=None,
        gt=0,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )
    category_id: int | None = None
    is_active: bool | None = None

class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    description: str | None
    image_url: str | None
    category_id: int | None
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: int
    name: ProductResponse
    model_config = ConfigDict(from_attributes=True)
class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: int
    status: str = "pending"
    created_at: datetime
    items: list[OrderItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=20)
class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str = Field(
        pattern="^(pending|confirmed|preparing|ready|completed|cancelled)$"
    )

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    model_config = ConfigDict(
        from_attributes=True
    )

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )
    sort_order: int = 0


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    is_active: bool
    sort_order: int
    model_config = ConfigDict(from_attributes=True)


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    slug: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    image_url: str | None = Field(
        default=None,
        max_length=500,
    )
    sort_order: int | None = None
    is_active: bool | None = None

class OrderStatusUpdate(BaseModel):
    new_status: str


