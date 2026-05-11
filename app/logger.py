import logging
import os
from logging.handlers import RotatingFileHandler

# ===============================
# 📁 PASTA DE LOG
# ===============================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "sistema.log")

# ===============================
# 🎯 CRIAR LOGGER
# ===============================
def get_logger(name: str = "app"):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # evita duplicação

    logger.setLevel(logging.INFO)

    # ===============================
    # 🧾 FORMATADOR
    # ===============================
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # ===============================
    # 📄 ARQUIVO COM ROTAÇÃO
    # ===============================
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2 * 1024 * 1024,  # 2MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # ===============================
    # 🖥️ CONSOLE
    # ===============================
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ===============================
    # 🔗 ADICIONA HANDLERS
    # ===============================
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger