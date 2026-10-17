from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.logger import logger
from app.models import Product, Category
from app.schemas import ProductCreate, ProductUpdate


def get_products(
    session: Session,
    category_id: int | None = None,
) -> list[Product]:
    logger.info(
        "Получение списка товаров. category_id=%s",
        category_id,
    )
    statement = (
    select(Product)
    .outerjoin(Category)
    .where(
        Product.is_active.is_(True),
        or_(
            Product.category_id.is_(None),
            Category.is_active.is_(True),
        ),
    )
    )
    if category_id is not None:
        statement = statement.where(
            Product.category_id == category_id
        )
    products = list(session.scalars(statement).all())
    logger.info(
        "Получено активных товаров: %s",
        len(products),
    )
    return products


def get_product(
    session: Session,
    product_id: int,
    include_inactive: bool = False,
) -> Product | None:
    product = session.get(Product, product_id)
    if product is None:
        return None
    if not include_inactive and not product.is_active:
        return None
    return product


def create_product(
    session: Session,
    product_data: ProductCreate,
) -> Product:
    if product_data.category_id is not None:
        category = session.get(
            Category,
            product_data.category_id,
        )
        if category is None:
            raise ValueError("Указанная категория не найдена")
        if not category.is_active:
            raise ValueError(
                "Нельзя добавить товар в неактивную категорию"
            )
    product_fields = product_data.model_dump()
    product = Product(**product_fields)
    try:
        session.add(product)
        session.commit()
        session.refresh(product)
    except Exception:
        session.rollback()
        raise
    logger.info(
        "Создан товар: id=%s, name=%s",
        product.id,
        product.name,
    )
    return product


def update_product(
    session: Session,
    product: Product,
    product_data: ProductUpdate,
) -> Product:
    update_fields = product_data.model_dump(exclude_unset=True)
    for field in ("name", "price"):
        if field in update_fields and update_fields[field] is None:
            raise ValueError(f"Поле {field} не может быть null")
    new_category_id = update_fields.get(
        "category_id",
        product.category_id,
    )
    if new_category_id is not None:
        category = session.get(Category, new_category_id)
        if category is None:
            raise ValueError("Указанная категория не найдена")
        if not category.is_active:
            raise ValueError("Нельзя назначить товар неактивной категории")
    for field, value in update_fields.items():
        setattr(product, field, value)
    try:
        session.commit()
        session.refresh(product)
    except Exception:
        session.rollback()
        raise

    logger.info("Обновлён товар: id=%s", product.id)
    return product