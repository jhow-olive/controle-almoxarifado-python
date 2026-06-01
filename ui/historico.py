from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QAbstractItemView
)
from PySide6.QtCore import Qt

from app.historico_service import listar_historico


class HistoricoWindow(QWidget):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario

        self.setWindowTitle("Histórico do Sistema")
        self.resize(1000, 600)

        self.setup_ui()
        self.carregar()

    # ==========================================
    # INTERFACE
    # ==========================================
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # TÍTULO
        titulo = QLabel("📜 Histórico do Sistema")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            margin: 10px;
        """)
        layout.addWidget(titulo)

        # BARRA SUPERIOR
        barra = QHBoxLayout()

        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Pesquisar usuário, ação ou descrição...")
        self.busca.textChanged.connect(self.filtrar_tabela)

        self.btn_atualizar = QPushButton("🔄 Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar)

        barra.addWidget(self.busca)
        barra.addWidget(self.btn_atualizar)

        layout.addLayout(barra)

        # TABELA
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Usuário",
            "Ação",
            "Descrição",
            "Data/Hora"
        ])

        # Ajustes visuais
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setSortingEnabled(True)

        # Ajuste automático
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.tabela)

        # STATUS
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("""
            padding: 5px;
            color: gray;
        """)
        layout.addWidget(self.lbl_status)

    # ==========================================
    # CARREGAR DADOS
    # ==========================================
    def carregar(self):
        try:
            dados = listar_historico()

            self.tabela.setSortingEnabled(False)
            self.tabela.clearContents()
            self.tabela.setRowCount(len(dados))

            for i, row in enumerate(dados):

                valores = [
                    str(row.get("id", "")),
                    str(row.get("usuario", "")),
                    str(row.get("acao", "")),
                    str(row.get("descricao", "")),
                    str(row.get("data_hora", ""))
                ]

                for j, valor in enumerate(valores):
                    item = QTableWidgetItem(valor)

                    # Centralizar algumas colunas
                    if j in [0, 1, 2, 4]:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.tabela.setItem(i, j, item)

            self.tabela.setSortingEnabled(True)

            self.lbl_status.setText(
                f"Total de registros: {len(dados)}"
            )

            # Aplicar filtro atual
            self.filtrar_tabela()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao carregar histórico:\n\n{str(e)}"
            )

    # ==========================================
    # FILTRO
    # ==========================================
    def filtrar_tabela(self):
        termo = self.busca.text().lower().strip()

        for linha in range(self.tabela.rowCount()):
            mostrar = False

            for coluna in range(self.tabela.columnCount()):
                item = self.tabela.item(linha, coluna)

                if item and termo in item.text().lower():
                    mostrar = True
                    break

            self.tabela.setRowHidden(linha, not mostrar)