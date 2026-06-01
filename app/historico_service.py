from app.db import conectar
from app.logger import get_logger


logger = get_logger(__name__)


def registrar(
    usuario_id,
    entidade,
    entidade_id,
    acao,
    dados_antes=None,
    dados_depois=None
):

    conn = conectar()

    try:

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO historico (
                usuario_id,
                entidade,
                entidade_id,
                acao,
                dados_antes,
                dados_depois
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            usuario_id,
            entidade,
            entidade_id,
            acao,
            dados_antes,
            dados_depois
        ))

        conn.commit()

    finally:
        conn.close()


def listar_historico():

    conn = conectar()

    try:

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                h.id,
                COALESCE(u.nome,'Sistema') usuario,
                h.entidade,
                h.acao,
                h.data_hora
            FROM historico h
            LEFT JOIN usuarios u
                ON u.id = h.usuario_id
            ORDER BY h.data_hora DESC
        """)

        return cur.fetchall()

    finally:
        conn.close()