import os

from datetime import datetime

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QFrame,
    QFileDialog
)

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Image,
    Paragraph,
    Spacer
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

from app.db import conectar


PADDING = 20


class RelatoriosWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Relatórios"
        )

        self.resize(420, 240)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            PADDING,
            PADDING,
            PADDING,
            PADDING
        )

        layout.setSpacing(15)

        titulo = QLabel(
            "📄 Relatórios do Sistema"
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

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

        box_layout = QVBoxLayout(box)

        box_layout.setContentsMargins(
            PADDING,
            PADDING,
            PADDING,
            PADDING
        )

        box_layout.setSpacing(12)

        self.btn = QPushButton(
            "📄 Gerar Estoque PDF"
        )

        self.btn.setMinimumHeight(42)

        self.btn.setCursor(
            Qt.PointingHandCursor
        )

        self.btn.clicked.connect(
            self.gerar_estoque
        )

        box_layout.addWidget(self.btn)

        layout.addWidget(box)

    def gerar_estoque(self):

        conn = None

        try:

            self.btn.setEnabled(False)

            nome_arquivo = (
                f"relatorio_estoque_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            arquivo, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Relatório",
                nome_arquivo,
                "PDF (*.pdf)"
            )

            if not arquivo:
                return

            doc = SimpleDocTemplate(
                arquivo,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=20
            )

            elementos = []

            styles = getSampleStyleSheet()

            # LOGO
            base_dir = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )

            caminho_logo = os.path.join(
                base_dir,
                "assets",
                "logo.jpg"
            )

            if os.path.exists(caminho_logo):

                logo = Image(
                    caminho_logo,
                    width=5 * cm,
                    height=2.2 * cm
                )

                elementos.append(logo)

            elementos.append(
                Spacer(1, 10)
            )

            # TÍTULO
            titulo = Paragraph(
                (
                    "<b>Relatório de Estoque</b>"
                    "<br/>"
                    f"Gerado em: "
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
                ),
                styles["Title"]
            )

            elementos.append(titulo)

            elementos.append(
                Spacer(1, 20)
            )

            # BANCO
            conn = conectar()

            cur = conn.cursor()

            cur.execute("""
                SELECT
                    codigo,
                    nome,
                    categoria,
                    quantidade_disponivel
                FROM materiais
                ORDER BY nome
            """)

            materiais = cur.fetchall()

            dados = [[
                "Código",
                "Nome",
                "Categoria",
                "Qtd"
            ]]

            for item in materiais:

                dados.append([
                    str(item[0]),
                    str(item[1]),
                    str(item[2]),
                    str(item[3])
                ])

            # TABELA
            tabela = Table(
                dados,
                colWidths=[
                    3 * cm,
                    7 * cm,
                    5 * cm,
                    2 * cm
                ]
            )

            tabela.setStyle(TableStyle([

                # HEADER
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937")
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),

                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    11
                ),

                # BODY
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.white
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#d1d5db")
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica"
                ),

                (
                    "FONTSIZE",
                    (0, 1),
                    (-1, -1),
                    10
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    10
                ),

                (
                    "TOPPADDING",
                    (0, 1),
                    (-1, -1),
                    6
                ),

                (
                    "BOTTOMPADDING",
                    (0, 1),
                    (-1, -1),
                    6
                ),

                (
                    "ALIGN",
                    (3, 1),
                    (3, -1),
                    "CENTER"
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),

            ]))

            elementos.append(tabela)

            elementos.append(
                Spacer(1, 20)
            )

            rodape = Paragraph(
                (
                    "Sistema de Controle "
                    "de Estoque"
                ),
                styles["Italic"]
            )

            elementos.append(rodape)

            doc.build(elementos)

            QMessageBox.information(
                self,
                "Sucesso",
                (
                    "Relatório PDF "
                    "gerado com sucesso!"
                )
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

        finally:

            if conn:
                conn.close()

            self.btn.setEnabled(True)