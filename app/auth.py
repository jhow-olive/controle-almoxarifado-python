from app.db import conectar
from app.logger import get_logger
import bcrypt
import time

logger = get_logger(__name__)

# 🔒 hash fake para evitar timing attack
FAKE_HASH = bcrypt.hashpw(
    b"fake_password",
    bcrypt.gensalt()
)


def verificar_login(login, senha):
    conn = None

    try:
        if not login or not senha:
            logger.warning(
                "Tentativa de login com campos vazios"
            )
            return None

        login = login.strip().lower()

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT id, nome, login, senha, tipo
            FROM usuarios
            WHERE login=%s
              AND ativo=1
        """, (login,))

        usuario = cur.fetchone()

        # 🔒 evita timing attack
        senha_hash = (
            usuario["senha"].encode("utf-8")
            if usuario else FAKE_HASH
        )

        senha_ok = bcrypt.checkpw(
            senha.encode("utf-8"),
            senha_hash
        )

        if not usuario or not senha_ok:
            logger.warning(f"Falha no login: {login}")

            time.sleep(0.5)  # 🔒 anti brute force

            return None

        # ✅ sucesso
        logger.info(
            f"Login realizado com sucesso: {login}"
        )

        return {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "login": usuario["login"],
            "tipo": usuario["tipo"]
        }

    except Exception as e:
        logger.error(f"Erro no login ({login}): {e}")
        return None

    finally:
        if conn:
            conn.close()