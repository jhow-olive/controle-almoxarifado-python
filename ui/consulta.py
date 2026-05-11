from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView
)

from PySide6.QtCore import Qt

from app.materiais_service import listar_materiais
from app.logger import get_logger

logger = get_logger(__name__)


class ConsultaMateriaisWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Consulta de Materiais")
        self.resize(1000, 600)

        self.setup_ui()
        self.carregar()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Campo busca
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("Pesquisar material...")
        self.busca.textChanged.connect(self.carregar)

        # Tabela
        self.tabela = QTableWidget()

        self.tabela.setColumnCount(7)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Código",
            "Nome",
            "Categoria",
            "Disponível",
            "Total",
            "Status"
        ])

        # Configurações UX
        self.tabela.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabela.setAlternatingRowColors(True)

        self.tabela.verticalHeader().setVisible(False)

        # Ajuste colunas
        header = self.tabela.horizontalHeader()

        header.setSectionResizeMode(QHeaderView.Stretch)

        # Layout
        layout.addWidget(self.busca)
        layout.addWidget(self.tabela)

    def carregar(self):
        try:
            termo = self.busca.text().strip().lower()

            materiais = listar_materiais()

            # Filtro busca
            if termo:
                materiais = [
                    m for m in materiais
                    if termo in (m.get("nome") or "").lower()
                    or termo in (m.get("codigo") or "").lower()
                    or termo in (m.get("categoria") or "").lower()
                ]

            self.tabela.setRowCount(len(materiais))

            for row, material in enumerate(materiais):

                dados = [
                    material.get("id"),
                    material.get("codigo"),
                    material.get("nome"),
                    material.get("categoria"),
                    material.get("quantidade_disponivel"),
                    material.get("quantidade_total"),
                    material.get("status")
                ]

                for col, valor in enumerate(dados):

                    item = QTableWidgetItem(str(valor))

                    # Centraliza números
                    if col in [0, 4, 5]:
                        item.setTextAlignment(Qt.AlignCenter)

                    self.tabela.setItem(row, col, item)

        except Exception as e:
            logger.error(f"Erro ao carregar materiais: {e}")

            QMessageBox.critical(
                self,
                "Erro",
                "Erro ao carregar materiais."
            )