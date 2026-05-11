import os
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox
)

from PySide6.QtGui import QIcon

from ui.login import LoginWindow

from app.style import get_style
from app.logger import get_logger


logger = get_logger(__name__)


APP_NAME = "Controle de Almoxarifado"
APP_THEME = "light"


def configurar_app(app):

    app.setApplicationName(
        APP_NAME
    )

    app.setStyle("Fusion")

    app.setStyleSheet(
        get_style(APP_THEME)
    )

    # ÍCONE
    caminho_icone = os.path.join(
        "assets",
        "icon.png"
    )

    if os.path.exists(caminho_icone):

        app.setWindowIcon(
            QIcon(caminho_icone)
        )


def main():

    app = None

    try:

        app = QApplication(sys.argv)

        configurar_app(app)

        logger.info(
            "Aplicação iniciada"
        )

        janela = LoginWindow()

        janela.show()

        sys.exit(app.exec())

    except Exception as e:

        logger.critical(
            f"Erro fatal aplicação: {e}"
        )

        # ERRO VISUAL
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


if __name__ == "__main__":
    main()