import os
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox
)

from PySide6.QtGui import (
    QIcon,
    QFont
)

from PySide6.QtCore import Qt

from ui.login import LoginWindow

from app.style import get_style
from app.logger import get_logger


# =====================================================
# LOGGER
# =====================================================
logger = get_logger(__name__)


# =====================================================
# CONFIGURAÇÕES
# =====================================================
APP_NAME = "Controle de Almoxarifado"

# "dark" ou "light"
APP_THEME = "dark"

APP_VERSION = "1.0.0"


# =====================================================
# RESOURCE PATH
# =====================================================
def resource_path(relative_path):

    try:

        base_path = sys._MEIPASS

    except Exception:

        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )


# =====================================================
# CONFIGURAR APP
# =====================================================
def configurar_app(app):

    # ==============================================
    # DADOS APP
    # ==============================================
    app.setApplicationName(APP_NAME)

    app.setApplicationVersion(APP_VERSION)

    app.setOrganizationName("CATENA")

    # ==============================================
    # ESTILO QT
    # ==============================================
    app.setStyle("Fusion")

    # ==============================================
    # FONTE GLOBAL
    # ==============================================
    fonte = QFont(
        "Segoe UI",
        10
    )

    app.setFont(fonte)

    # ==============================================
    # TEMA
    # ==============================================
    app.setStyleSheet(
        get_style(APP_THEME)
    )

    # ==============================================
    # ÍCONE
    # ==============================================
    caminho_icone = resource_path(
        "assets/icon.png"
    )

    if os.path.exists(caminho_icone):

        app.setWindowIcon(
            QIcon(caminho_icone)
        )

    # ==============================================
    # CURSOR
    # ==============================================
    app.setCursorFlashTime(1000)


# =====================================================
# MAIN
# =====================================================
def main():

    app = None

    try:

        # ==========================================
        # QApplication
        # ==========================================
        app = QApplication(sys.argv)

        configurar_app(app)

        logger.info(
            f"{APP_NAME} iniciado"
        )

        # ==========================================
        # LOGIN
        # ==========================================
        janela = LoginWindow()

        janela.show()

        # ==========================================
        # EXEC
        # ==========================================
        sys.exit(app.exec())

    except Exception as e:

        logger.critical(
            f"Erro fatal aplicação: {e}"
        )

        # ==========================================
        # ERRO VISUAL
        # ==========================================
        if app:

            QMessageBox.critical(
                None,
                "Erro Fatal",
                (
                    "Ocorreu um erro fatal "
                    "na aplicação.\n\n"
                    f"{str(e)}"
                )
            )

        raise


# =====================================================
# START
# =====================================================
if __name__ == "__main__":

    main()