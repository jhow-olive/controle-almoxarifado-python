from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QFrame
)

from app.movimentacao_service import (
    criar_saida,
    adicionar_item_saida
)

from app.materiais_service import listar_materiais
from app.db import conectar


PADDING = 20


class SaidaWindow(QWidget):

    def __init__(self, usuario):
        super().__init__()

        self.usuario = usuario

        self.setWindowTitle("Nova Saída")
        self.resize(500, 420)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(15)

        titulo = QLabel("🚚 Registrar Saída")

        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size:20pt;
            font-weight:bold;
        """)

        layout.addWidget(titulo)

        box = QFrame()

        box.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #e5e7eb;
                border-radius:14px;
            }
        """)

        form = QVBoxLayout(box)

        form.setContentsMargins(
            PADDING,
            PADDING,
            PADDING,
            PADDING
        )

        form.setSpacing(12)

        # VEÍCULO
        form.addWidget(QLabel("Veículo"))

        self.cb_veiculo = QComboBox()

        self.cb_veiculo.wheelEvent = (
            lambda e: None
        )

        form.addWidget(self.cb_veiculo)

        # MATERIAL
        form.addWidget(QLabel("Material"))

        self.cb_material = QComboBox()

        self.cb_material.wheelEvent = (
            lambda e: None
        )

        form.addWidget(self.cb_material)

        # QUANTIDADE
        form.addWidget(QLabel("Quantidade"))

        self.txt_qtd = QLineEdit()

        self.txt_qtd.setPlaceholderText(
            "Quantidade"
        )

        self.txt_qtd.setValidator(
            QIntValidator(1, 999999)
        )

        form.addWidget(self.txt_qtd)

        # BOTÃO
        self.btn_salvar = QPushButton(
            "Registrar Saída"
        )

        self.btn_salvar.setMinimumHeight(40)

        self.btn_salvar.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_salvar.clicked.connect(
            self.salvar
        )

        form.addWidget(self.btn_salvar)

        layout.addWidget(box)

        self.carregar_veiculos()
        self.carregar_materiais()

    def atualizar_estado_botao(self):

        self.btn_salvar.setEnabled(
            self.cb_veiculo.count() > 0
            and
            self.cb_material.count() > 0
        )

    def carregar_veiculos(self):

        self.cb_veiculo.clear()

        conn = None

        try:
            conn = conectar()

            cur = conn.cursor(
                dictionary=True
            )

            cur.execute("""
                SELECT id, placa, descricao
                FROM veiculos
                ORDER BY placa
            """)

            veiculos = cur.fetchall()

            for v in veiculos:

                self.cb_veiculo.addItem(
                    f"{v['placa']} • "
                    f"{v['descricao']}",
                    v["id"]
                )

            self.atualizar_estado_botao()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

        finally:

            if conn:
                conn.close()

    def carregar_materiais(self):

        self.cb_material.clear()

        try:
            materiais = listar_materiais()

            for m in materiais:

                nome = m[2]
                qtd = m[4]

                self.cb_material.addItem(
                    f"{nome} "
                    f"(Disponível: {qtd})",
                    m[0]
                )

            self.atualizar_estado_botao()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

    def salvar(self):

        veiculo_id = (
            self.cb_veiculo.currentData()
        )

        material_id = (
            self.cb_material.currentData()
        )

        qtd = self.txt_qtd.text().strip()

        if not veiculo_id:

            QMessageBox.warning(
                self,
                "Erro",
                "Selecione um veículo."
            )

            return

        if not material_id:

            QMessageBox.warning(
                self,
                "Erro",
                "Selecione um material."
            )

            return

        if not qtd:

            QMessageBox.warning(
                self,
                "Erro",
                "Quantidade inválida."
            )

            return

        quantidade = int(qtd)

        resposta = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja registrar esta saída?"
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:

            self.btn_salvar.setEnabled(False)

            saida_id = criar_saida(
                self.usuario["id"],
                veiculo_id
            )

            ok = adicionar_item_saida(
                saida_id,
                material_id,
                quantidade
            )

            if ok:

                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Saída registrada!"
                )

                self.cb_material.setCurrentIndex(0)

                self.txt_qtd.clear()

                self.txt_qtd.setFocus()

                self.close()

            else:

                QMessageBox.warning(
                    self,
                    "Erro",
                    "Estoque insuficiente."
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

        finally:

            self.atualizar_estado_botao()