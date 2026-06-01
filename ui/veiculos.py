from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox
)

from app.db import conectar


class VeiculosWindow(QWidget):

    def __init__(self, usuario=None):
        super().__init__()

        self.usuario = usuario

        self.setWindowTitle("Veículos")
        self.resize(900, 600)

        self.layout = QVBoxLayout(self)

        titulo = QLabel("🚚 Cadastro de Veículos")
        self.layout.addWidget(titulo)

        form_layout = QHBoxLayout()

        self.edt_placa = QLineEdit()
        self.edt_placa.setPlaceholderText("Placa")

        self.edt_descricao = QLineEdit()
        self.edt_descricao.setPlaceholderText("Descrição")

        form_layout.addWidget(self.edt_placa)
        form_layout.addWidget(self.edt_descricao)

        self.layout.addLayout(form_layout)

        botoes = QHBoxLayout()

        self.btn_salvar = QPushButton("Salvar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_atualizar = QPushButton("Atualizar")

        botoes.addWidget(self.btn_salvar)
        botoes.addWidget(self.btn_excluir)
        botoes.addWidget(self.btn_atualizar)

        self.layout.addLayout(botoes)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(
            ["ID", "Placa", "Descrição"]
        )

        self.layout.addWidget(self.tabela)

        self.id_selecionado = None

        self.btn_salvar.clicked.connect(self.salvar)
        self.btn_excluir.clicked.connect(self.excluir)
        self.btn_atualizar.clicked.connect(self.carregar_dados)

        self.tabela.cellClicked.connect(
            self.selecionar_linha
        )

        self.carregar_dados()

    def carregar_dados(self):

        try:

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, placa, descricao
                FROM veiculos
                ORDER BY placa
            """)

            dados = cursor.fetchall()

            self.tabela.setRowCount(len(dados))

            for linha, registro in enumerate(dados):

                for coluna, valor in enumerate(registro):

                    self.tabela.setItem(
                        linha,
                        coluna,
                        QTableWidgetItem(str(valor))
                    )

            conn.close()

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )

    def salvar(self):

        placa = self.edt_placa.text().strip()
        descricao = self.edt_descricao.text().strip()

        if not placa:

            QMessageBox.warning(
                self,
                "Aviso",
                "Informe a placa."
            )
            return

        try:

            conn = conectar()
            cursor = conn.cursor()

            if self.id_selecionado:

                cursor.execute("""
                    UPDATE veiculos
                    SET placa=%s,
                        descricao=%s
                    WHERE id=%s
                """, (
                    placa,
                    descricao,
                    self.id_selecionado
                ))

            else:

                cursor.execute("""
                    INSERT INTO veiculos
                    (placa, descricao)
                    VALUES (%s,%s)
                """, (
                    placa,
                    descricao
                ))

            conn.commit()
            conn.close()

            self.limpar()
            self.carregar_dados()

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )

    def excluir(self):

        if not self.id_selecionado:
            return

        try:

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM veiculos
                WHERE id=%s
            """, (
                self.id_selecionado,
            ))

            conn.commit()
            conn.close()

            self.limpar()
            self.carregar_dados()

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                str(erro)
            )

    def selecionar_linha(self, row, column):

        self.id_selecionado = int(
            self.tabela.item(row, 0).text()
        )

        self.edt_placa.setText(
            self.tabela.item(row, 1).text()
        )

        self.edt_descricao.setText(
            self.tabela.item(row, 2).text()
        )

    def limpar(self):

        self.id_selecionado = None

        self.edt_placa.clear()
        self.edt_descricao.clear()