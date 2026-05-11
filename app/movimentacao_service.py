from app.db import conectar
from app.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# 🚚 CRIAR SAÍDA
# =========================================================

def criar_saida(
    usuario_id,
    veiculo_id,
    responsavel=None
):

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO saidas (

                usuario_id,
                veiculo_id,
                responsavel

            )
            VALUES (%s,%s,%s)
        """, (

            usuario_id,
            veiculo_id,
            responsavel

        ))

        saida_id = cur.lastrowid

        conn.commit()

        logger.info(
            f"Saída criada: {saida_id}"
        )

        return saida_id

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao criar saída: {e}"
        )

        return None

    finally:

        if conn:
            conn.close()


# =========================================================
# 📦 ADICIONAR ITEM NA SAÍDA
# =========================================================

def adicionar_item_saida(
    saida_id,
    material_id,
    quantidade
):

    if not isinstance(quantidade, int):

        logger.warning(
            "Quantidade inválida"
        )

        return False

    if quantidade <= 0:

        logger.warning(
            "Quantidade deve ser maior que zero"
        )

        return False

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # =====================================
        # 🔒 LOCK MATERIAL
        # =====================================

        cur.execute("""
            SELECT

                id,
                nome,
                quantidade_total,
                quantidade_disponivel,
                status

            FROM materiais
            WHERE id = %s
            FOR UPDATE
        """, (material_id,))

        material = cur.fetchone()

        if not material:

            logger.warning(
                f"Material não encontrado: {material_id}"
            )

            return False

        # =====================================
        # ❌ estoque insuficiente
        # =====================================

        if material["quantidade_disponivel"] < quantidade:

            logger.warning(
                f"Estoque insuficiente: "
                f"{material['nome']}"
            )

            return False

        # =====================================
        # 📦 inserir item
        # =====================================

        cur.execute("""
            INSERT INTO saida_itens (

                saida_id,
                material_id,
                quantidade

            )
            VALUES (%s,%s,%s)
        """, (

            saida_id,
            material_id,
            quantidade

        ))

        item_saida_id = cur.lastrowid

        # =====================================
        # 📉 atualizar estoque
        # =====================================

        nova_quantidade = (
            material["quantidade_disponivel"] -
            quantidade
        )

        novo_status = (
            "DISPONIVEL"
            if nova_quantidade > 0
            else "INDISPONIVEL"
        )

        cur.execute("""
            UPDATE materiais
            SET

                quantidade_disponivel = %s,
                status = %s

            WHERE id = %s
        """, (

            nova_quantidade,
            novo_status,
            material_id

        ))

        # =====================================
        # 📊 registrar movimentação
        # =====================================

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
            "SAIDA",
            quantidade,
            saida_id

        ))

        conn.commit()

        logger.info(
            f"Item adicionado na saída "
            f"{saida_id}"
        )

        return item_saida_id

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro ao adicionar item saída: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()


# =========================================================
# 🔄 RETORNAR ITEM
# =========================================================

def retornar_item(
    item_id,
    quantidade
):

    if not isinstance(quantidade, int):

        logger.warning(
            "Quantidade inválida no retorno"
        )

        return False

    if quantidade <= 0:

        logger.warning(
            "Quantidade retorno <= 0"
        )

        return False

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # =====================================
        # 🔒 LOCK ITEM SAÍDA
        # =====================================

        cur.execute("""
            SELECT

                si.id,
                si.material_id,
                si.quantidade,
                si.retornado,

                m.nome,
                m.quantidade_disponivel

            FROM saida_itens si

            INNER JOIN materiais m
            ON m.id = si.material_id

            WHERE si.id = %s
            FOR UPDATE
        """, (item_id,))

        item = cur.fetchone()

        if not item:

            logger.warning(
                f"Item saída não encontrado: {item_id}"
            )

            return False

        # =====================================
        # 🔒 validar retorno
        # =====================================

        saldo_restante = (
            item["quantidade"] -
            item["retornado"]
        )

        if quantidade > saldo_restante:

            logger.warning(
                "Retorno maior que saldo pendente"
            )

            return False

        # =====================================
        # 📦 atualizar retorno item
        # =====================================

        novo_retorno = (
            item["retornado"] +
            quantidade
        )

        cur.execute("""
            UPDATE saida_itens
            SET retornado = %s
            WHERE id = %s
        """, (

            novo_retorno,
            item_id

        ))

        # =====================================
        # 📈 devolver estoque
        # =====================================

        nova_disponivel = (
            item["quantidade_disponivel"] +
            quantidade
        )

        cur.execute("""
            UPDATE materiais
            SET

                quantidade_disponivel = %s,
                status = 'DISPONIVEL'

            WHERE id = %s
        """, (

            nova_disponivel,
            item["material_id"]

        ))

        # =====================================
        # 📊 registrar movimentação
        # =====================================

        cur.execute("""
            INSERT INTO movimentacoes_estoque (

                material_id,
                tipo,
                quantidade,
                referencia_id

            )
            VALUES (%s,%s,%s,%s)
        """, (

            item["material_id"],
            "RETORNO",
            quantidade,
            item_id

        ))

        conn.commit()

        logger.info(
            f"Retorno realizado item {item_id}"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro retorno item: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()


# =========================================================
# 📋 LISTAR SAÍDAS
# =========================================================

def listar_saidas():

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT

                s.id,
                s.usuario_id,
                s.veiculo_id,
                s.responsavel,
                s.data_saida,
                s.data_retorno,
                s.status,

                u.nome AS usuario,

                v.placa,
                v.descricao

            FROM saidas s

            INNER JOIN usuarios u
            ON u.id = s.usuario_id

            INNER JOIN veiculos v
            ON v.id = s.veiculo_id

            ORDER BY s.data_saida DESC
        """)

        return cur.fetchall()

    except Exception as e:

        logger.error(
            f"Erro listar saídas: {e}"
        )

        return []

    finally:

        if conn:
            conn.close()


# =========================================================
# 📋 LISTAR ITENS DA SAÍDA
# =========================================================

def listar_itens_saida(saida_id):

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT

                si.id,
                si.quantidade,
                si.retornado,

                m.id AS material_id,
                m.codigo,
                m.nome,
                m.categoria

            FROM saida_itens si

            INNER JOIN materiais m
            ON m.id = si.material_id

            WHERE si.saida_id = %s

            ORDER BY m.nome
        """, (saida_id,))

        return cur.fetchall()

    except Exception as e:

        logger.error(
            f"Erro listar itens saída: {e}"
        )

        return []

    finally:

        if conn:
            conn.close()

# =========================================================
# 📋 LISTAR SAÍDAS ABERTAS
# =========================================================

def listar_saidas_abertas():

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT

                s.id,
                s.usuario_id,
                s.veiculo_id,
                s.responsavel,
                s.data_saida,
                s.status,

                u.nome AS usuario,

                v.placa,
                v.descricao

            FROM saidas s

            INNER JOIN usuarios u
            ON u.id = s.usuario_id

            INNER JOIN veiculos v
            ON v.id = s.veiculo_id

            WHERE s.status = 'ABERTA'

            ORDER BY s.data_saida DESC
        """)

        return cur.fetchall()

    except Exception as e:

        logger.error(
            f"Erro listar saídas abertas: {e}"
        )

        return []

    finally:

        if conn:
            conn.close()

itens_saida = listar_itens_saida

# =========================================================
# 🔒 FECHAR SAÍDA
# =========================================================

def fechar_saida(saida_id):

    conn = None

    try:

        conn = conectar()

        cur = conn.cursor(dictionary=True)

        # =====================================
        # verificar itens pendentes
        # =====================================

        cur.execute("""
            SELECT

                id,
                quantidade,
                retornado

            FROM saida_itens

            WHERE saida_id = %s
        """, (saida_id,))

        itens = cur.fetchall()

        if not itens:

            logger.warning(
                f"Saída sem itens: {saida_id}"
            )

        for item in itens:

            saldo = (
                item["quantidade"] -
                item["retornado"]
            )

            if saldo > 0:

                logger.warning(
                    f"Saída possui itens pendentes: "
                    f"{saida_id}"
                )

                return False

        # =====================================
        # fechar saída
        # =====================================

        cur.execute("""
            UPDATE saidas
            SET

                status = 'FECHADA',
                data_retorno = NOW()

            WHERE id = %s
        """, (saida_id,))

        conn.commit()

        logger.info(
            f"Saída fechada: {saida_id}"
        )

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        logger.error(
            f"Erro fechar saída: {e}"
        )

        return False

    finally:

        if conn:
            conn.close()