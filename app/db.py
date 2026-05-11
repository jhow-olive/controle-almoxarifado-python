import time
import mysql.connector

from mysql.connector import Error

from config import DB_CONFIG
from app.logger import get_logger


logger = get_logger(__name__)


def conectar(retry=3, delay=2):
    """
    Cria conexão com retry automático.
    """

    for tentativa in range(1, retry + 1):

        try:
            conn = mysql.connector.connect(
                **DB_CONFIG,
                connection_timeout=5,
                autocommit=False
            )

            if conn.is_connected():

                logger.info(
                    "Conexão com banco estabelecida"
                )

                return conn

        except Error as e:

            logger.error(
                f"Erro conexão DB "
                f"(tentativa {tentativa}/{retry}): {e}"
            )

            if tentativa < retry:
                time.sleep(delay)

    # ❌ falha total
    logger.critical(
        "Não foi possível conectar ao banco de dados"
    )

    raise ConnectionError(
        "Não foi possível conectar ao banco."
    )