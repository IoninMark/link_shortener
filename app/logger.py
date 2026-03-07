import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys


log_dir = Path("app/logs")
log_dir.mkdir(exist_ok=True)

LOG_FORMAT = (
    "[%(asctime)s][%(name)s: line %(lineno)d func:%(funcName)s] "
    "%(levelname)s: %(message)s"
)
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


def setup_logger(
        name: str,
        log_file: str = "app.log",
) -> logging.Logger:
    """Настройка логгера с ротацией файлов."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Удаляем все существующие обработчики, если они есть.
    logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Создаем обработчик для файла с ротацией логов
    file_handler = RotatingFileHandler(
        log_dir / log_file,
        maxBytes=MAX_LOG_FILE_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Создаем обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


# Создаем основные логгеры
app_logger = setup_logger("app", "app.log")
db_logger = setup_logger("database", "database.log")
api_logger = setup_logger("api", "api.log")
