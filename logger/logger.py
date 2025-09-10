import logging
from logging.handlers import RotatingFileHandler
import os

# Папка для логов
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Создаём общий логгер
logger = logging.getLogger("SiteResponseBot")
logger.setLevel(logging.DEBUG)

# Обработчик с ротацией по размеру
file_handler = RotatingFileHandler(
    filename=os.path.join(log_dir, "project.log"),
    maxBytes=1 * 1024 * 1024,  # 1 МБ
    backupCount=7,             # хранить 7 старых файлов
    encoding="utf-8"
)

# Формат логов
formatter = logging.Formatter(
    '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(funcName)s()\n     %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Добавляем обработчик
logger.addHandler(file_handler)

# Пример записи
logger.info("Программа запущена")
