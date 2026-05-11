import os
import shutil
import subprocess
from datetime import datetime

from config import DB_CONFIG
from app.logger import get_logger

logger = get_logger(__name__)


BACKUP_DIR = "backup"


def gerar_backup():
    try:
        # ===============================
        # 📁 cria pasta
        # ===============================
        os.makedirs(BACKUP_DIR, exist_ok=True)

        # ===============================
        # 📄 nome do arquivo
        # ===============================
        arquivo = datetime.now().strftime(
            "%Y%m%d_%H%M%S.sql"
        )

        destino = os.path.join(
            BACKUP_DIR,
            arquivo
        )

        # ===============================
        # 🔒 dados do banco
        # ===============================
        user = DB_CONFIG["user"]
        password = DB_CONFIG["password"]
        database = DB_CONFIG["database"]
        host = DB_CONFIG.get("host", "localhost")

        # ===============================
        # 🔍 localizar mysqldump
        # ===============================
        mysqldump = shutil.which("mysqldump")

        if not mysqldump:
            logger.error(
                "mysqldump não encontrado no PATH"
            )
            return None

        # ===============================
        # 🔒 variável ambiente
        # evita senha aparecer no processo
        # ===============================
        env = os.environ.copy()
        env["MYSQL_PWD"] = password

        comando = [
            mysqldump,
            f"-h{host}",
            f"-u{user}",
            database,
            "--single-transaction",
            "--routines",
            "--triggers",
            "--default-character-set=utf8mb4"
        ]

        logger.info(
            f"Iniciando backup do banco: {database}"
        )

        # ===============================
        # 🚀 executa backup
        # ===============================
        with open(destino, "w", encoding="utf-8") as f:

            resultado = subprocess.run(
                comando,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                timeout=120,
                check=True
            )

        # ===============================
        # ✅ valida arquivo
        # ===============================
        if not os.path.exists(destino):
            logger.error(
                "Arquivo de backup não foi criado"
            )
            return None

        tamanho = os.path.getsize(destino)

        if tamanho == 0:
            logger.error(
                "Backup gerado está vazio"
            )
            return None

        logger.info(
            f"Backup gerado com sucesso: {destino}"
        )

        return destino

    except subprocess.TimeoutExpired:
        logger.error(
            "Tempo excedido ao gerar backup"
        )
        return None

    except subprocess.CalledProcessError as e:
        logger.error(
            f"Erro no mysqldump: {e.stderr}"
        )
        return None

    except Exception as e:
        logger.exception(
            f"Erro inesperado ao gerar backup: {e}"
        )
        return None