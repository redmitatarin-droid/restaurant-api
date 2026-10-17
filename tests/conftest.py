import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import Base, User
from app.security import get_current_user, require_admin


# SQLite в памяти — отдельная от PostgreSQL, живёт только во время тестов.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Перед каждым тестом — чистые таблицы в SQLite."""
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def test_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_session):
    """TestClient, у которого get_session возвращает сессию SQLite."""
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user():
    return User(
        id=1,
        name="Admin",
        email="admin@example.com",
        password_hash="x",
        role="admin",
    )


@pytest.fixture
def client_as_admin(admin_user, test_session):
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[require_admin] = lambda: admin_user
    app.dependency_overrides[get_current_user] = lambda: admin_user

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()