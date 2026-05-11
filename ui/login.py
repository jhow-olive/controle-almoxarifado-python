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
    QApplication,
    QGraphicsDropShadowEffect
)

from PySide6.QtGui import (
    QPixmap,
    QIcon,
    QColor
)

from PySide6.QtCore import Qt

from app.auth import verificar_login


# ==================================================
# RESOURCE PATH
# ==================================================
def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS

    except Exception:

        base_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                ".."
            )
        )

    return os.path.join(
        base_path,
        relative_path
    )


# ==================================================
# LOGIN WINDOW
# ==================================================
class LoginWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setup_ui()

    # ==================================================
    # UI
    # ==================================================
    def setup_ui(self):

        self.setWindowTitle(
            "Sistema Almoxarifado"
        )

        self.resize(500, 620)

        self.setStyleSheet("""
            QWidget {
                background-color: #0F172A;
                font-family: Segoe UI;
                color: white;
            }
        """)

        # ==================================================
        # ÍCONE
        # ==================================================
        icon_path = resource_path(
            "assets/logo.ico"
        )

        if os.path.exists(icon_path):

            self.setWindowIcon(
                QIcon(icon_path)
            )

        # ==================================================
        # LAYOUT PRINCIPAL
        # ==================================================
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            40,
            40,
            40,
            40
        )

        layout.setSpacing(20)

        layout.addStretch()

        # ==================================================
        # CARD LOGIN
        # ==================================================
        card = QFrame()

        card.setObjectName("card")

        card.setFixedWidth(420)

        card.setStyleSheet("""
            QFrame#card {
                background-color: #111827;
                border-radius: 24px;
                border: 1px solid #1F2937;
            }

            QLineEdit {
                background-color: #1F2937;
                border: 1px solid #374151;
                border-radius: 14px;
                padding: 14px;
                font-size: 14px;
                color: white;
            }

            QLineEdit:focus {
                border: 2px solid #2563EB;
            }

            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 14px;
                padding: 14px;
                font-size: 15px;
                font-weight: bold;
                color: white;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)

        # ==================================================
        # SOMBRA
        # ==================================================
        sombra = QGraphicsDropShadowEffect()

        sombra.setBlurRadius(35)

        sombra.setOffset(0, 0)

        sombra.setColor(
            QColor(0, 0, 0, 180)
        )

        card.setGraphicsEffect(sombra)

        # ==================================================
        # LAYOUT CARD
        # ==================================================
        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            40,
            40,
            40,
            40
        )

        card_layout.setSpacing(18)

        # ==================================================
        # LOGO
        # ==================================================
        self.logo = QLabel()

        self.logo.setAlignment(
            Qt.AlignCenter
        )

        caminho_logo = resource_path(
            "assets/logo.jpg"
        )

        if os.path.exists(caminho_logo):

            pixmap = QPixmap(
                caminho_logo
            )

            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    260,
                    160,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.logo.setPixmap(
                    pixmap
                )

        else:

            self.logo.setText("CATENA")

            self.logo.setStyleSheet("""
                font-size: 34px;
                font-weight: bold;
                color: #2563EB;
            """)

        card_layout.addWidget(self.logo)

        # ==================================================
        # TÍTULO
        # ==================================================
        titulo = QLabel(
            "Sistema de Almoxarifado"
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)

        card_layout.addWidget(titulo)

        # ==================================================
        # SUBTÍTULO
        # ==================================================
        subtitulo = QLabel(
            "Controle inteligente de materiais"
        )

        subtitulo.setAlignment(
            Qt.AlignCenter
        )

        subtitulo.setStyleSheet("""
            color: #9CA3AF;
            font-size: 13px;
            margin-bottom: 15px;
        """)

        card_layout.addWidget(subtitulo)

        # ==================================================
        # LOGIN
        # ==================================================
        self.txt_login = QLineEdit()

        self.txt_login.setPlaceholderText(
            "Usuário"
        )

        card_layout.addWidget(
            self.txt_login
        )

        # ==================================================
        # SENHA
        # ==================================================
        self.txt_senha = QLineEdit()

        self.txt_senha.setPlaceholderText(
            "Senha"
        )

        self.txt_senha.setEchoMode(
            QLineEdit.Password
        )

        card_layout.addWidget(
            self.txt_senha
        )

        # ==================================================
        # BOTÃO
        # ==================================================
        self.btn_login = QPushButton(
            "🔐 Entrar"
        )

        self.btn_login.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_login.clicked.connect(
            self.logar
        )

        card_layout.addWidget(
            self.btn_login
        )

        # ==================================================
        # RODAPÉ
        # ==================================================
        rodape = QLabel(
            "© CATENA Tecnologia"
        )

        rodape.setAlignment(
            Qt.AlignCenter
        )

        rodape.setStyleSheet("""
            color: #6B7280;
            font-size: 11px;
            margin-top: 10px;
        """)

        card_layout.addWidget(
            rodape
        )

        # ==================================================
        # ENTER
        # ==================================================
        self.txt_login.returnPressed.connect(
            self.logar
        )

        self.txt_senha.returnPressed.connect(
            self.logar
        )

        # ==================================================
        # CENTRALIZAÇÃO
        # ==================================================
        hbox = QHBoxLayout()

        hbox.addStretch()

        hbox.addWidget(card)

        hbox.addStretch()

        layout.addLayout(hbox)

        layout.addStretch()

        # ==================================================
        # FOCO
        # ==================================================
        self.txt_login.setFocus()

    # ==================================================
    # LOGIN
    # ==================================================
    def logar(self):

        usuario_texto = (
            self.txt_login.text().strip()
        )

        senha_texto = (
            self.txt_senha.text()
        )

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

            QApplication.setOverrideCursor(
                Qt.WaitCursor
            )

            usuario = verificar_login(
                usuario_texto,
                senha_texto
            )

            QApplication.restoreOverrideCursor()

            if usuario:

                from ui.dashboard import DashboardWindow

                self.dashboard = DashboardWindow(
                    usuario
                )

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