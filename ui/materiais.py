from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QFrame,
    QAbstractItemView
)

from PySide6.QtCore import Qt

from app.db import conectar


class MateriaisWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Materiais")
        self.resize(1200, 700)

        self.setup_ui()
        self.carregar_dados()

    # ==========================================
    # INTERFACE
    # ==========================================
    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ==========================================
        # TÍTULO
        # ==========================================
        titulo = QLabel("📦 Cadastro de Materiais")

        titulo.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #111827;
        """)

        layout.addWidget(titulo)

        # ==========================================
        # FORMULÁRIO
        # ==========================================
        box = QFrame()

        box.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
            }

            QLineEdit {
                padding: 10px;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 2px solid #2563eb;
            }

            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #1d4ed8;
            }
        """)

        form = QHBoxLayout(box)

        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(10)

        # ==========================================
        # CAMPOS
        # ==========================================
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Código")

        self.txt_nome = QLineEdit()
        self.txt_nome.setPlaceholderText("Nome do material")

        self.txt_categoria = QLineEdit()
        self.txt_categoria.setPlaceholderText("Categoria")

        self.txt_qtd = QLineEdit()
        self.txt_qtd.setPlaceholderText("Quantidade")

        self.btn_add = QPushButton("💾 Salvar")
        self.btn_add.clicked.connect(self.salvar)

        form.addWidget(self.txt_codigo)
        form.addWidget(self.txt_nome)
        form.addWidget(self.txt_categoria)
        form.addWidget(self.txt_qtd)
        form.addWidget(self.btn_add)

        layout.addWidget(box)

        # ==========================================
        # PESQUISA
        # ==========================================
        self.busca = QLineEdit()

        self.busca.setPlaceholderText(
            "🔍 Pesquisar material..."
        )

        self.busca.textChanged.connect(self.filtrar_tabela)

        layout.addWidget(self.busca)

        # ==========================================
        # TABELA
        # ==========================================
        self.tabela = QTableWidget()

        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Código",
            "Nome",
            "Categoria",
            "Qtd"
        ])

        # VISUAL
        self.tabela.setAlternatingRowColors(True)

        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela.setSortingEnabled(True)

        # COLUNAS
        header = self.tabela.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        layout.addWidget(self.tabela)

        # ==========================================
        # BOTÕES
        # ==========================================
        botoes = QHBoxLayout()

        self.btn_excluir = QPushButton("🗑 Excluir")
        self.btn_excluir.clicked.connect(self.excluir)

        self.btn_atualizar = QPushButton("🔄 Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_dados)

        botoes.addWidget(self.btn_excluir)
        botoes.addWidget(self.btn_atualizar)
        botoes.addStretch()

        layout.addLayout(botoes)

        # ==========================================
        # STATUS
        # ==========================================
        self.lbl_status = QLabel("")

        self.lbl_status.setStyleSheet("""
            color: gray;
            padding: 5px;
        """)

        layout.addWidget(self.lbl_status)

        # ENTER salva
        self.txt_qtd.returnPressed.connect(self.salvar)

    # ==========================================
    # CARREGAR DADOS
    # ==========================================
    def carregar_dados(self):

        self.tabela.setSortingEnabled(False)
        self.tabela.setRowCount(0)

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    codigo,
                    nome,
                    categoria,
                    quantidade_disponivel
                FROM materiais
                ORDER BY id DESC
            """)

            dados = cur.fetchall()

            self.tabela.setRowCount(len(dados))

            for linha, row in enumerate(dados):

                for coluna, valor in enumerate(row):

                    item = QTableWidgetItem(str(valor))

                    if coluna in [0, 4]:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.tabela.setItem(
                        linha,
                        coluna,
                        item
                    )

            conn.close()

            self.tabela.setSortingEnabled(True)

            self.lbl_status.setText(
                f"Total de materiais: {len(dados)}"
            )

            self.filtrar_tabela()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao carregar materiais:\n\n{str(e)}"
            )

    # ==========================================
    # SALVAR
    # ==========================================
    def salvar(self):

        codigo = self.txt_codigo.text().strip()
        nome = self.txt_nome.text().strip()
        categoria = self.txt_categoria.text().strip()
        qtd = self.txt_qtd.text().strip()

        # VALIDAÇÕES
        if not codigo:
            QMessageBox.warning(
                self,
                "Atenção",
                "Digite o código."
            )
            self.txt_codigo.setFocus()
            return

        if not nome:
            QMessageBox.warning(
                self,
                "Atenção",
                "Digite o nome do material."
            )
            self.txt_nome.setFocus()
            return

        if not qtd:
            QMessageBox.warning(
                self,
                "Atenção",
                "Digite a quantidade."
            )
            self.txt_qtd.setFocus()
            return

        try:
            qtd_int = int(qtd)

            if qtd_int < 0:
                QMessageBox.warning(
                    self,
                    "Erro",
                    "Quantidade inválida."
                )
                return

        except ValueError:
            QMessageBox.warning(
                self,
                "Erro",
                "Quantidade deve ser numérica."
            )
            return

        try:
            conn = conectar()
            cur = conn.cursor()

            # VERIFICA DUPLICADO
            cur.execute(
                "SELECT id FROM materiais WHERE codigo=%s",
                (codigo,)
            )

            if cur.fetchone():

                QMessageBox.warning(
                    self,
                    "Atenção",
                    "Código já cadastrado."
                )

                conn.close()
                return

            # INSERT
            cur.execute("""
                INSERT INTO materiais (
                    codigo,
                    nome,
                    categoria,
                    quantidade_total,
                    quantidade_disponivel
                )
                VALUES (%s,%s,%s,%s,%s)
            """, (
                codigo,
                nome,
                categoria,
                qtd_int,
                qtd_int
            ))

            conn.commit()
            conn.close()

            QMessageBox.information(
                self,
                "Sucesso",
                "Material cadastrado com sucesso."
            )

            self.limpar_campos()

            self.carregar_dados()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao salvar:\n\n{str(e)}"
            )

    # ==========================================
    # EXCLUIR
    # ==========================================
    def excluir(self):

        linha = self.tabela.currentRow()

        if linha < 0:

            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um material."
            )

            return

        item_id = self.tabela.item(linha, 0).text()
        nome = self.tabela.item(linha, 2).text()

        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja excluir:\n\n{nome} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute(
                "DELETE FROM materiais WHERE id=%s",
                (item_id,)
            )

            conn.commit()
            conn.close()

            QMessageBox.information(
                self,
                "Sucesso",
                "Material excluído."
            )

            self.carregar_dados()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao excluir:\n\n{str(e)}"
            )

    # ==========================================
    # FILTRO
    # ==========================================
    def filtrar_tabela(self):

        termo = self.busca.text().lower().strip()

        for linha in range(self.tabela.rowCount()):

            mostrar = False

            for coluna in range(
                self.tabela.columnCount()
            ):

                item = self.tabela.item(linha, coluna)

                if item and termo in item.text().lower():
                    mostrar = True
                    break

            self.tabela.setRowHidden(
                linha,
                not mostrar
            )

    # ==========================================
    # LIMPAR CAMPOS
    # ==========================================
    def limpar_campos(self):

        self.txt_codigo.clear()
        self.txt_nome.clear()
        self.txt_categoria.clear()
        self.txt_qtd.clear()

        self.txt_codigo.setFocus()