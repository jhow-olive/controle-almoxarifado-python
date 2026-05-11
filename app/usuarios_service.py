from app.db import conectar
from app.logger import get_logger
import bcrypt

logger = get_logger(__name__)


def listar_usuarios():
    conn = conectar()

    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                id,
                nome,
                login,
                tipo,
                ativo,
                criado_em
            FROM usuarios
            ORDER BY nome
        """)

        return cur.fetchall()

    except Exception as e:
        logger.error(f"Erro ao listar usuários: {e}")
        return []

    finally:
        conn.close()


def buscar_usuario_por_login(login):
    conn = conectar()

    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT *
            FROM usuarios
            WHERE login = %s
            AND ativo = 1
        """, (login,))

        return cur.fetchone()

    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None

    finally:
        conn.close()


def criar_usuario(nome, login, senha, tipo="USUARIO"):
    if not nome or not login or not senha:
        raise ValueError("Dados obrigatórios não informados")

    if tipo not in ["ADMIN", "USUARIO"]:
        raise ValueError("Tipo inválido")

    conn = conectar()

    try:
        cur = conn.cursor()

        # Verifica duplicidade
        cur.execute("""
            SELECT id
            FROM usuarios
            WHERE login = %s
        """, (login,))

        if cur.fetchone():
            logger.warning("Login já existe")
            return False

        # Hash senha
        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cur.execute("""
            INSERT INTO usuarios (
                nome,
                login,
                senha,
                tipo,
                ativo
            )
            VALUES (%s, %s, %s, %s, 1)
        """, (
            nome,
            login,
            senha_hash,
            tipo
        ))

        conn.commit()

        logger.info(f"Usuário criado: {login}")

        return True

    except Exception as e:
        logger.error(f"Erro ao criar usuário: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def validar_login(login, senha):
    try:
        usuario = buscar_usuario_por_login(login)

        if not usuario:
            return None

        senha_ok = bcrypt.checkpw(
            senha.encode("utf-8"),
            usuario["senha"].encode("utf-8")
        )

        if not senha_ok:
            logger.warning(f"Tentativa login inválido: {login}")
            return None

        return usuario

    except Exception as e:
        logger.error(f"Erro validação login: {e}")
        return None


def editar_usuario(usuario_id, nome, login, tipo):
    if not nome or not login:
        return False

    if tipo not in ["ADMIN", "USUARIO"]:
        return False

    conn = conectar()

    try:
        cur = conn.cursor()

        # Evita login duplicado
        cur.execute("""
            SELECT id
            FROM usuarios
            WHERE login = %s
            AND id <> %s
        """, (login, usuario_id))

        if cur.fetchone():
            logger.warning("Login já em uso")
            return False

        cur.execute("""
            UPDATE usuarios
            SET
                nome = %s,
                login = %s,
                tipo = %s
            WHERE id = %s
        """, (
            nome,
            login,
            tipo,
            usuario_id
        ))

        conn.commit()

        logger.info(f"Usuário atualizado ID={usuario_id}")

        return True

    except Exception as e:
        logger.error(f"Erro ao editar usuário: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def alterar_senha(usuario_id, nova_senha):
    if not nova_senha:
        return False

    conn = conectar()

    try:
        cur = conn.cursor()

        senha_hash = bcrypt.hashpw(
            nova_senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cur.execute("""
            UPDATE usuarios
            SET senha = %s
            WHERE id = %s
        """, (
            senha_hash,
            usuario_id
        ))

        conn.commit()

        logger.info(f"Senha alterada ID={usuario_id}")

        return True

    except Exception as e:
        logger.error(f"Erro alterar senha: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def excluir_usuario(usuario_id, usuario_logado_id=None):
    conn = conectar()

    try:
        cur = conn.cursor()

        # Impede excluir a si mesmo
        if usuario_id == usuario_logado_id:
            logger.warning("Usuário tentou excluir a si mesmo")
            return False

        # Busca usuário
        cur.execute("""
            SELECT tipo
            FROM usuarios
            WHERE id = %s
        """, (usuario_id,))

        user = cur.fetchone()

        if not user:
            logger.warning("Usuário não encontrado")
            return False

        # Protege último ADMIN
        if user[0] == "ADMIN":

            cur.execute("""
                SELECT COUNT(*)
                FROM usuarios
                WHERE tipo = 'ADMIN'
                AND ativo = 1
            """)

            total_admin = cur.fetchone()[0]

            if total_admin <= 1:
                logger.warning("Tentativa remover último ADMIN")
                return False

        # Soft delete
        cur.execute("""
            UPDATE usuarios
            SET ativo = 0
            WHERE id = %s
        """, (usuario_id,))

        conn.commit()

        logger.info(f"Usuário desativado ID={usuario_id}")

        return True

    except Exception as e:
        logger.error(f"Erro ao excluir usuário: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()