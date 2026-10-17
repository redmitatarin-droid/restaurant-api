from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


def get_active_categories(session: Session) -> list[Category]:
    statement = (
        select(Category)
        .where(Category.is_active == True)  # noqa: E712
        .order_by(Category.sort_order, Category.id)
    )
    result = session.scalars(statement)
    return list(result.all())


def get_all_categories(session: Session) -> list[Category]:
    statement = select(Category).order_by(
        Category.sort_order,
        Category.id,
    )
    result = session.scalars(statement)
    return list(result.all())

def get_category_by_id(
    session: Session,
    category_id: int,
) -> Category | None:
    return session.get(Category, category_id)


def create_category(
    session: Session,
    category_data: CategoryCreate,
) -> Category:
    existing_category = session.scalar(
        select(Category).where(
            (Category.name == category_data.name)
            | (Category.slug == category_data.slug)
        )
    )
    if existing_category is not None:
        raise ValueError(
            "Категория с таким названием или slug уже существует"
        )

    category_fields = category_data.model_dump() #как работает модель дамп

    category = Category(**category_fields)

    session.add(category)
    session.commit()

    session.refresh(category)

    return category


def update_category(
    session: Session,
    category: Category,
    category_data: CategoryUpdate,
) -> Category:
    update_fields = category_data.model_dump(
        exclude_unset=True
    )
    for field in ("name", "slug"):
        if field in update_fields and update_fields[field] is None:
            raise ValueError(
                f"Поле {field} не может быть пустым"
            )
    new_name = update_fields.get("name", category.name)
    new_slug = update_fields.get("slug", category.slug)
    duplicate = session.scalar(
        select(Category).where(
            (
                (Category.name == new_name)
                | (Category.slug == new_slug)
            )
            & (Category.id != category.id)
        )
    )
    if duplicate is not None:
        raise ValueError(
            "Другая категория уже использует это название или slug"
        )
    for field, value in update_fields.items():
        setattr(category, field, value)
    session.commit()
    session.refresh(category)
    return category