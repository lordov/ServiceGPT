import logging

# Создаём логгер
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Формат логов
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Логирование в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Логирование в файл
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Добавляем обработчики в логгер
logger.addHandler(console_handler)
logger.addHandler(file_handler)
