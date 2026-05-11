from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QLabel,
    QHBoxLayout,
    QListWidgetItem,
    QAbstractItemView
)
from PySide6.QtCore import Qt

from app.listas_service import criar_lista, listar_listas


class ListasWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Listas Modelo")
        self.resize(600, 500)

        self.setup_ui()
        self.carregar()

    # ==========================================
    # INTERFACE
    # ==========================================
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # TÍTULO
        titulo = QLabel("📋 Listas Modelo")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            margin: 10px;
        """)
        layout.addWidget(titulo)

        # CAMPO + BOTÃO
        linha = QHBoxLayout()

        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Digite o nome da lista...")
        self.nome.returnPressed.connect(self.salvar)

        self.btn_criar = QPushButton("➕ Criar Lista")
        self.btn_criar.clicked.connect(self.salvar)

        linha.addWidget(self.nome)
        linha.addWidget(self.btn_criar)

        layout.addLayout(linha)

        # CAMPO DE PESQUISA
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("🔍 Pesquisar listas...")
        self.busca.textChanged.connect(self.filtrar)

        layout.addWidget(self.busca)

        # LISTA
        self.lista = QListWidget()
        self.lista.setAlternatingRowColors(True)
        self.lista.setSelectionMode(QAbstractItemView.SingleSelection)

        layout.addWidget(self.lista)

        # STATUS
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("""
            color: gray;
            padding: 5px;
        """)
        layout.addWidget(self.lbl_status)

    # ==========================================
    # CARREGAR LISTAS
    # ==========================================
    def carregar(self):
        try:
            self.lista.clear()

            dados = listar_listas()

            for item in dados:
                texto = f"{item[0]} - {item[1]}"

                widget_item = QListWidgetItem(texto)
                widget_item.setTextAlignment(Qt.AlignLeft)

                self.lista.addItem(widget_item)

            self.lbl_status.setText(
                f"Total de listas: {len(dados)}"
            )

            self.filtrar()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao carregar listas:\n\n{str(e)}"
            )

    # ==========================================
    # SALVAR LISTA
    # ==========================================
    def salvar(self):
        try:
            nome = self.nome.text().strip()

            # VALIDAÇÃO
            if not nome:
                QMessageBox.warning(
                    self,
                    "Atenção",
                    "Digite o nome da lista."
                )
                return

            if len(nome) < 3:
                QMessageBox.warning(
                    self,
                    "Atenção",
                    "O nome deve ter pelo menos 3 caracteres."
                )
                return

            criar_lista(nome)

            QMessageBox.information(
                self,
                "Sucesso",
                "Lista criada com sucesso."
            )

            self.nome.clear()
            self.carregar()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao salvar lista:\n\n{str(e)}"
            )

    # ==========================================
    # FILTRAR LISTA
    # ==========================================
    def filtrar(self):
        termo = self.busca.text().lower().strip()

        for i in range(self.lista.count()):
            item = self.lista.item(i)

            mostrar = termo in item.text().lower()

            item.setHidden(not mostrar)