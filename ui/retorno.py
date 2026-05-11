from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QFrame
)

from app.movimentacao_service import (
    listar_saidas_abertas,
    listar_itens_saida,
    retornar_item,
    fechar_saida
)


class RetornoWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Retorno de Materiais")
        self.resize(500, 430)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        titulo = QLabel("↩ Registrar Retorno")
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
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(12)

        # SAÍDA
        form.addWidget(QLabel("Saída aberta"))

        self.cb_saida = QComboBox()

        self.cb_saida.currentIndexChanged.connect(
            self.atualizar_itens
        )

        form.addWidget(self.cb_saida)

        # ITEM
        form.addWidget(QLabel("Item"))

        self.cb_item = QComboBox()

        form.addWidget(self.cb_item)

        # QUANTIDADE
        form.addWidget(QLabel("Quantidade devolvida"))

        self.txt_qtd = QLineEdit()

        self.txt_qtd.setPlaceholderText(
            "Quantidade devolvida"
        )

        self.txt_qtd.setValidator(
            QIntValidator(1, 999999)
        )

        form.addWidget(self.txt_qtd)

        # BOTÃO CONFIRMAR
        self.btn_confirmar = QPushButton(
            "Confirmar Retorno"
        )

        self.btn_confirmar.setMinimumHeight(40)

        self.btn_confirmar.clicked.connect(
            self.confirmar
        )

        form.addWidget(self.btn_confirmar)

        # BOTÃO FECHAR
        self.btn_fechar = QPushButton(
            "Fechar Saída"
        )

        self.btn_fechar.setMinimumHeight(40)

        self.btn_fechar.clicked.connect(
            self.fechar
        )

        form.addWidget(self.btn_fechar)

        layout.addWidget(box)

        self.carregar_saidas()

    def carregar_saidas(self):
        self.cb_saida.clear()

        try:
            saidas = listar_saidas_abertas()

            for s in saidas:
                self.cb_saida.addItem(
                    f"Saída #{s[0]} • {s[1]}",
                    s[0]
                )

            self.btn_fechar.setEnabled(
                self.cb_saida.count() > 0
            )

            self.atualizar_itens()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

    def atualizar_itens(self):
        self.cb_item.clear()

        saida_id = self.cb_saida.currentData()

        if not saida_id:
            self.btn_confirmar.setEnabled(False)
            return

        try:
            for i in listar_itens_saida(saida_id):

                restante = (
                    int(i[2]) - int(i[3])
                )

                if restante > 0:

                    self.cb_item.addItem(
                        f"{i[1]} "
                        f"(Restante: {restante})",
                        i[0]
                    )

            self.btn_confirmar.setEnabled(
                self.cb_item.count() > 0
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

    def confirmar(self):
        item_id = self.cb_item.currentData()

        qtd = self.txt_qtd.text().strip()

        if not item_id:
            QMessageBox.warning(
                self,
                "Erro",
                "Selecione um item."
            )
            return

        if not qtd.isdigit() or int(qtd) <= 0:
            QMessageBox.warning(
                self,
                "Erro",
                "Quantidade inválida."
            )
            return

        try:
            ok = retornar_item(
                item_id,
                int(qtd)
            )

            if ok:

                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Retorno registrado!"
                )

                self.txt_qtd.clear()

                self.atualizar_itens()

            else:

                QMessageBox.warning(
                    self,
                    "Erro",
                    "Não foi possível retornar."
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

    def fechar(self):
        saida_id = self.cb_saida.currentData()

        if not saida_id:
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja realmente fechar esta saída?"
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            ok = fechar_saida(saida_id)

            if ok:

                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Saída fechada!"
                )

                self.txt_qtd.clear()

                self.carregar_saidas()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )