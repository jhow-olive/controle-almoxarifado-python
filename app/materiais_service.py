from app.db import conectar
from app.logger import get_logger


# =========================================================
# 🪵 LOGGER
# =========================================================

logger = get_logger(__name__)


# =========================================================
# 📦 LISTAR MATERIAIS
# =========================================================

def listar_materiais():

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                id,
                codigo,
                nome,
                categoria,
                quantidade_total,
                quantidade_disponivel,
                status,
                localizacao,
                observacao,
                criado_em
            FROM materiais
            ORDER BY nome
        """)

        materiais = cur.fetchall()

        return materiais

    except Exception as e:

        logger.error(
            f"Erro ao listar materiais: {e}"
        )

        return []

    finally:

        if conn:
            conn.close()


# =========================================================
# 📦 BUSCAR MATERIAL
# =========================================================

def buscar_material(material_id):

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT *
            FROM materiais
            WHERE id = %s
        """, (material_id,))

        return cur.fetchone()

    except Exception as e:

        logger.error(
            f"Erro ao buscar material: {e}"
        )

        return None

    finally:

        if conn:
            conn.close()


# =========================================================
# 📦 CRIAR MATERIAL
# =========================================================

def criar_material(
    codigo,
    nome,
    categoria,
    quantidade,
    localizacao=None,
    observacao=None
):

    if not codigo or not nome:

        raise ValueError(
            "Código e nome são obrigatórios"
        )

    if not isinstance(quantidade, int):

        raise ValueError(
            "Quantidade inválida"
        )

    if quantidade < 0:

        raise ValueError(
            "Quantidade não pode ser negativa"
        )

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # =====================================
        # 🔒 validar código duplicado
        # =====================================

        cur.execute("""
            SELECT id
            FROM materiais
            WHERE codigo = %s
        """, (codigo,))

        existe = cur.fetchone()

        if existe:

            logger.warning(
                f"Código já existe: {codigo}"
            )

            return False

        # =====================================
        # 📦 status automático
        # =====================================

        status = (
            "DISPONIVEL"
            if quantidade > 0
            else "INDISPONIVEL"
        )

        # =====================================
        # 💾 inserir material
        # =====================================

        cur.execute("""
            INSERT INTO materiais (

                codigo,
                nome,
                categoria,
                quantidade_total,
                quantidade_disponivel,
                status,
                localizacao,
                observacao

            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (

            codigo,
            nome,
            categoria,
            quantidade,
            quantidade,
            status,
            localizacao,
            observacao

        ))

        material_id = cur.lastrowid

        # =====================================
        # 📊 movimentação inicial
        # =====================================

        if quantidade > 0:

            cur.execute("""
                INSERT INTO movimentacoes_estoque (

                    material_id,
                    tipo,
                    quantidade,
                    referencia_id

                )
                VALUES (%s,%s,%s,%s)
            """, (

                material_id,
                "ENTRADA",
                quantidade,
                material_id

            ))

        conn.commit()

        logger.info(
            f"Material criado: {nome}"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao criar material: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()


# =========================================================
# 📦 EDITAR MATERIAL
# =========================================================

def editar_material(
    material_id,
    codigo,
    nome,
    categoria,
    quantidade,
    localizacao=None,
    observacao=None
):

    if not codigo or not nome:

        return False

    if not isinstance(quantidade, int):

        return False

    if quantidade < 0:

        return False

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # =====================================
        # 🔒 lock do material
        # =====================================

        cur.execute("""
            SELECT
                quantidade_total,
                quantidade_disponivel
            FROM materiais
            WHERE id = %s
            FOR UPDATE
        """, (material_id,))

        material = cur.fetchone()

        if not material:

            return False

        # =====================================
        # 🔒 validar código duplicado
        # =====================================

        cur.execute("""
            SELECT id
            FROM materiais
            WHERE codigo = %s
            AND id != %s
        """, (

            codigo,
            material_id

        ))

        existe = cur.fetchone()

        if existe:

            logger.warning(
                f"Código duplicado: {codigo}"
            )

            return False

        # =====================================
        # 📦 calcular diferença
        # =====================================

        diferenca = (
            quantidade -
            material["quantidade_total"]
        )

        nova_disponivel = (
            material["quantidade_disponivel"] +
            diferenca
        )

        # =====================================
        # ❌ impedir estoque negativo
        # =====================================

        if nova_disponivel < 0:

            logger.warning(
                "Tentativa de estoque negativo"
            )

            return False

        status = (
            "DISPONIVEL"
            if nova_disponivel > 0
            else "INDISPONIVEL"
        )

        # =====================================
        # 💾 atualizar material
        # =====================================

        cur.execute("""
            UPDATE materiais
            SET

                codigo = %s,
                nome = %s,
                categoria = %s,

                quantidade_total = %s,
                quantidade_disponivel = %s,

                status = %s,

                localizacao = %s,
                observacao = %s

            WHERE id = %s
        """, (

            codigo,
            nome,
            categoria,

            quantidade,
            nova_disponivel,

            status,

            localizacao,
            observacao,

            material_id

        ))

        # =====================================
        # 📊 registrar movimentação
        # =====================================

        if diferenca != 0:

            tipo = (
                "ENTRADA"
                if diferenca > 0
                else "SAIDA"
            )

            cur.execute("""
                INSERT INTO movimentacoes_estoque (

                    material_id,
                    tipo,
                    quantidade,
                    referencia_id

                )
                VALUES (%s,%s,%s,%s)
            """, (

                material_id,
                tipo,
                abs(diferenca),
                material_id

            ))

        conn.commit()

        logger.info(
            f"Material atualizado: {material_id}"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao editar material: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()


# =========================================================
# 📦 EXCLUIR MATERIAL
# =========================================================

def excluir_material(material_id):

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # =====================================
        # 🔒 validar uso em saída
        # =====================================

        cur.execute("""
            SELECT COUNT(*) AS total
            FROM saida_itens
            WHERE material_id = %s
        """, (material_id,))

        uso_saida = cur.fetchone()["total"]

        # =====================================
        # 🔒 validar uso em listas
        # =====================================

        cur.execute("""
            SELECT COUNT(*) AS total
            FROM listas_modelo_itens
            WHERE material_id = %s
        """, (material_id,))

        uso_lista = cur.fetchone()["total"]

        # =====================================
        # ❌ impedir exclusão
        # =====================================

        if uso_saida > 0 or uso_lista > 0:

            logger.warning(
                f"Material em uso: {material_id}"
            )

            return False

        # =====================================
        # 🗑 excluir
        # =====================================

        cur.execute("""
            DELETE FROM materiais
            WHERE id = %s
        """, (material_id,))

        conn.commit()

        logger.info(
            f"Material excluído: {material_id}"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao excluir material: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()