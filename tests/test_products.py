from fastapi.testclient import TestClient
from app.models import User
from app.security import get_current_user
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.models import User
from app.security import get_current_user, require_admin

@pytest.fixture
def admin_user():
    return User(
        id=1,
        name="Admin",
        email="admin@example.com",
        password_hash="not-a-real-hash",
        role="admin",
    )

@pytest.fixture
def client_as_admin(admin_user):
    app.dependency_overrides[require_admin] = lambda: admin_user
    # на всякий случай, потому что require_admin зависит от get_current_user
    app.dependency_overrides[get_current_user] = lambda: admin_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_me_returns_current_user(client_as_admin):
    # Arrange: создаём тестового пользователя.
    # Для этого теста не требуется записывать его в БД.
    test_user = User(
        id=100,
        name="Test User",
        email="test@example.com",
        password_hash="not-a-real-password-hash",
        role="customer"
    )
    # Подменяем зависимость, которая обычно проверяет JWT.
    # Теперь endpoint получит именно нашего тестового пользователя.
    app.dependency_overrides[get_current_user] = (
        lambda: test_user
    )
    # Act: отправляем запрос к профилю.
    response = client_as_admin.get("/users/me")
    # Assert: проверяем статус и публичные данные.
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 100
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    # Пароль или его хеш не должны попадать в ответ.
    assert "password_hash" not in data
    assert "password" not in data


def test_get_products_returns_empty_list(client_as_admin):
    # Act: запрашиваем список товаров.
    response = client_as_admin.get("/products")

    # Assert: проверяем статус и содержимое ответа.
    assert response.status_code == 200
    assert response.json() == []

def test_create_product(client_as_admin):
    # Arrange: готовим JSON для создания товара.
    payload = {
        "name": "Pizza",
        "price": 500
    }

    # Act: отправляем POST-запрос.
    response = client_as_admin.post(
        "/products",
        json=payload
    )

    # Assert: проверяем результат.
    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["name"] == "Pizza"
    assert data["price"] == 500


def test_create_product_rejects_negative_price(client_as_admin):
    payload = {
        "name": "Pizza",
        "price": -100
    }

    response = client_as_admin.post(
        "/products",
        json=payload
    )

    # FastAPI/Pydantic отклоняет невалидное тело.
    assert response.status_code == 422


def test_create_product_rejects_missing_name(client_as_admin):
    payload = {
        "price": 500
    }

    response = client_as_admin.post(
        "/products",
        json=payload
    )

    assert response.status_code == 422



def test_get_me_without_token_returns_401(client):
    # В этом тесте get_current_user не подменяется.
    # Поэтому FastAPI использует настоящую проверку JWT.
    response = client.get("/users/me")

    assert response.status_code == 401