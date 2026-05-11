import sys
import os

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QFrame,
    QHBoxLayout,
    QApplication
)

from PySide6.QtGui import (
    QPixmap,
    QIcon
)

from PySide6.QtCore import Qt

from app.auth import verificar_login


# ==========================================
# RESOURCE PATH
# ==========================================
def resource_path(relative_path):
    """
    Retorna caminho absoluto compatível
    com ambiente dev e executável (.exe)
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

    return os.path.join(base_path, relative_path)


# ==========================================
# LOGIN WINDOW
# ==========================================
class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    # ==========================================
    # INTERFACE
    # ==========================================
    def setup_ui(self):

        self.setWindowTitle("Sistema Almoxarifado")
        self.resize(450, 500)

        # ÍCONE
        icon_path = resource_path("assets/logo.ico")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # LAYOUT PRINCIPAL
        layout = QVBoxLayout(self)

        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        # ==========================================
        # CARD
        # ==========================================
        card = QFrame()

        card.setObjectName("card")

        card.setStyleSheet("""
            QWidget {
                background-color: #f3f4f6;
            }

            QFrame#card {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #d1d5db;
            }

            QLineEdit {
                padding: 12px;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                font-size: 14px;
                background: white;
            }

            QLineEdit:focus {
                border: 2px solid #2563eb;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(18)

        # ==========================================
        # LOGO
        # ==========================================
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignCenter)

        caminho_logo = resource_path("assets/logo.jpg")

        if os.path.exists(caminho_logo):

            pixmap = QPixmap(caminho_logo)

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    250,
                    150,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.logo.setPixmap(pixmap)

            else:
                self.logo.setText("ERRO AO CARREGAR LOGO")
                self.logo.setStyleSheet("""
                    color: red;
                    font-weight: bold;
                    font-size: 16px;
                """)

        else:
            self.logo.setText("CATENA")
            self.logo.setStyleSheet("""
                font-size: 28px;
                font-weight: bold;
                color: #111827;
            """)

        card_layout.addWidget(self.logo)

        # ==========================================
        # TÍTULO
        # ==========================================
        titulo = QLabel("Sistema de Almoxarifado")

        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #111827;
        """)

        card_layout.addWidget(titulo)

        # ==========================================
        # SUBTÍTULO
        # ==========================================
        subtitulo = QLabel(
            "Controle de materiais, saídas e estoque"
        )

        subtitulo.setAlignment(Qt.AlignCenter)

        subtitulo.setStyleSheet("""
            color: #6b7280;
            font-size: 12px;
            margin-bottom: 10px;
        """)

        card_layout.addWidget(subtitulo)

        # ==========================================
        # LOGIN
        # ==========================================
        self.txt_login = QLineEdit()

        self.txt_login.setPlaceholderText("Digite seu usuário")

        card_layout.addWidget(self.txt_login)

        # ==========================================
        # SENHA
        # ==========================================
        self.txt_senha = QLineEdit()

        self.txt_senha.setPlaceholderText("Digite sua senha")

        self.txt_senha.setEchoMode(QLineEdit.Password)

        card_layout.addWidget(self.txt_senha)

        # ==========================================
        # BOTÃO LOGIN
        # ==========================================
        self.btn_login = QPushButton("🔐 Entrar")

        self.btn_login.setCursor(Qt.PointingHandCursor)

        self.btn_login.clicked.connect(self.logar)

        card_layout.addWidget(self.btn_login)

        # ==========================================
        # RODAPÉ
        # ==========================================
        rodape = QLabel("© CATENA Tecnologia")

        rodape.setAlignment(Qt.AlignCenter)

        rodape.setStyleSheet("""
            color: #9ca3af;
            font-size: 11px;
            margin-top: 5px;
        """)

        card_layout.addWidget(rodape)

        # ==========================================
        # ENTER
        # ==========================================
        self.txt_login.returnPressed.connect(self.logar)
        self.txt_senha.returnPressed.connect(self.logar)

        # ==========================================
        # CENTRALIZAÇÃO
        # ==========================================
        layout.addStretch()

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(card)
        hbox.addStretch()

        layout.addLayout(hbox)

        layout.addStretch()

        # Foco inicial
        self.txt_login.setFocus()

    # ==========================================
    # LOGIN
    # ==========================================
    def logar(self):

        usuario_texto = self.txt_login.text().strip()
        senha_texto = self.txt_senha.text()

        # VALIDAÇÕES
        if not usuario_texto:
            QMessageBox.warning(
                self,
                "Atenção",
                "Digite o usuário."
            )
            self.txt_login.setFocus()
            return

        if not senha_texto:
            QMessageBox.warning(
                self,
                "Atenção",
                "Digite a senha."
            )
            self.txt_senha.setFocus()
            return

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            usuario = verificar_login(
                usuario_texto,
                senha_texto
            )

            QApplication.restoreOverrideCursor()

            if usuario:

                from ui.dashboard import DashboardWindow

                self.dashboard = DashboardWindow(usuario)

                self.dashboard.show()

                self.close()

            else:

                QMessageBox.warning(
                    self,
                    "Login inválido",
                    "Usuário ou senha incorretos."
                )

                self.txt_senha.clear()
                self.txt_senha.setFocus()

        except Exception as e:

            QApplication.restoreOverrideCursor()

            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao realizar login:\n\n{str(e)}"
            )