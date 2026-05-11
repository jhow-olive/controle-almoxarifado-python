import os

from dotenv import load_dotenv


# CARREGA VARIÁVEIS DO .env
load_dotenv()


DB_CONFIG = {
    "host": os.getenv(
        "DB_HOST",
        "localhost"
    ),

    "user": os.getenv(
        "DB_USER",
        "root"
    ),

    "password": os.getenv(
        "DB_PASSWORD"
    ),

    "database": os.getenv(
        "DB_NAME",
        "almoxarifado"
    ),

    "port": int(
        os.getenv(
            "DB_PORT",
            3306
        )
    )
}


# VALIDA SENHA
if not DB_CONFIG["password"]:

    raise ValueError(
        "DB_PASSWORD não definido no arquivo .env"
    )