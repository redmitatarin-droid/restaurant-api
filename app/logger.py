import logging

# Создаём логгер именно для нашего приложения.
logger = logging.getLogger("restaurant_api")

# Уровень INFO означает, что мы увидим информационные
# сообщения, предупреждения и ошибки.
logger.setLevel(logging.INFO)

# Формат каждой записи: время, уровень, имя логгера, сообщение.
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Записываем сообщения в консоль.
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем обработчик только один раз,
# чтобы при повторном импорте не дублировать записи.
if not logger.handlers:
    logger.addHandler(console_handler)