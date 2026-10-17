
import os
from dotenv import load_dotenv

# Загружаем значения из .env в переменные окружения.
# По умолчанию ищется файл .env в текущей рабочей директории.
load_dotenv()


def get_required_setting(name: str) -> str:
    # Читаем значение настройки по её имени.
    value = os.getenv(name)

    # Если настройка отсутствует или пустая,
    # останавливаем запуск с понятной ошибкой.
    if not value:
        raise RuntimeError(f"Required setting is missing: {name}")

    return value
DATABASE_URL = get_required_setting("DATABASE_URL")
SECRET_KEY = get_required_setting("SECRET_KEY")

# Для локальной разработки можно указать значение по умолчанию.
# В опубликованном приложении нужно задать реальный origin фронтенда.
FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://127.0.0.1:5500"
)

PUBLIC_REGISTRATION_ENABLED = (
    os.getenv("PUBLIC_REGISTRATION_ENABLED", "false").lower()
    in {"true", "1", "yes"}
)