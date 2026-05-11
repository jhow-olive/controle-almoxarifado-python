from app.db import conectar
from app.logger import get_logger


logger = get_logger(__name__)


def criar_lista(nome):

    # ===============================
    # ✅ validação
    # ===============================
    if not nome or not nome.strip():

        logger.warning(
            "Tentativa de criar lista com nome vazio"
        )

        return False

    nome = nome.strip()

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # ===============================
        # 🔍 evitar duplicidade
        # ===============================
        cur.execute(
            """
            SELECT id
            FROM listas_modelo
            WHERE nome = %s
            """,
            (nome,)
        )

        if cur.fetchone():

            logger.warning(
                f"Lista já existe: {nome}"
            )

            return False

        # ===============================
        # 💾 inserir lista
        # ===============================
        cur.execute(
            """
            INSERT INTO listas_modelo (nome)
            VALUES (%s)
            """,
            (nome,)
        )

        conn.commit()

        logger.info(
            f"Lista criada: {nome}"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao criar lista: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()


def adicionar_item_lista(
    lista_id,
    material_id,
    quantidade
):

    # ===============================
    # ✅ validação quantidade
    # ===============================
    try:

        quantidade = int(quantidade)

        if quantidade <= 0:

            logger.warning(
                "Quantidade inválida"
            )

            return False

    except (ValueError, TypeError):

        logger.warning(
            "Quantidade não numérica"
        )

        return False

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # ===============================
        # 🔍 validar lista
        # ===============================
        cur.execute(
            """
            SELECT id
            FROM listas_modelo
            WHERE id = %s
            """,
            (lista_id,)
        )

        if not cur.fetchone():

            logger.warning(
                f"Lista inexistente: {lista_id}"
            )

            return False

        # ===============================
        # 🔍 validar material
        # ===============================
        cur.execute(
            """
            SELECT id
            FROM materiais
            WHERE id = %s
            """,
            (material_id,)
        )

        if not cur.fetchone():

            logger.warning(
                f"Material inexistente: {material_id}"
            )

            return False

        # ===============================
        # 🔍 verificar item duplicado
        # ===============================
        cur.execute(
            """
            SELECT id
            FROM listas_modelo_itens
            WHERE lista_id = %s
              AND material_id = %s
            """,
            (
                lista_id,
                material_id
            )
        )

        if cur.fetchone():

            logger.warning(
                "Material já existe na lista"
            )

            return False

        # ===============================
        # 💾 inserir item
        # ===============================
        cur.execute(
            """
            INSERT INTO listas_modelo_itens (
                lista_id,
                material_id,
                quantidade
            )
            VALUES (%s, %s, %s)
            """,
            (
                lista_id,
                material_id,
                quantidade
            )
        )

        conn.commit()

        logger.info(
            f"Item adicionado à lista "
            f"{lista_id} "
            f"(material {material_id})"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao adicionar item: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()


def listar_listas():

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT
                id,
                nome
            FROM listas_modelo
            ORDER BY nome
            """
        )

        dados = cur.fetchall()

        logger.info(
            f"{len(dados)} listas carregadas"
        )

        return dados

    except Exception as e:

        logger.error(
            f"Erro ao listar listas: {e}"
        )

        return []

    finally:

        if conn:
            conn.close()