from app.db import conectar
from app.logger import get_logger


logger = get_logger(__name__)


def registrar(usuario_id, acao, descricao):
    conn = None

    try:
        conn = conectar()

        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO historico (
                usuario_id,
                acao,
                descricao
            )
            VALUES (%s, %s, %s)
            """,
            (
                usuario_id,
                acao,
                descricao
            )
        )

        conn.commit()

        logger.info(
            f"Histórico registrado: {acao}"
        )

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao registrar histórico: {e}"
        )

    finally:

        if conn:
            conn.close()


def listar_historico():
    conn = None

    try:
        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT
                h.id,
                COALESCE(u.nome, 'Sistema') AS usuario,
                h.acao,
                h.descricao,
                h.data_hora
            FROM historico h
            LEFT JOIN usuarios u
                ON u.id = h.usuario_id
            ORDER BY h.data_hora DESC
            """
        )

        dados = cur.fetchall()

        logger.info(
            f"Histórico carregado: {len(dados)} registros"
        )

        return dados

    except Exception as e:

        logger.error(
            f"Erro ao listar histórico: {e}"
        )

        return []

    finally:

        if conn:
            conn.close()