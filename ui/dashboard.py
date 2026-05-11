import os
import sys
import tempfile
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox,
    QDateEdit
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QDate

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from reportlab.platypus import (
    SimpleDocTemplate,
    Image,
    Spacer,
    Paragraph
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from ui.saidas import SaidaWindow
from ui.retorno import RetornoWindow
from ui.historico import HistoricoWindow

from app.backup import gerar_backup
from app.db import conectar
from app.logger import get_logger

logger = get_logger(__name__)


# =====================================================
# 📊 DADOS DO GRÁFICO
# =====================================================
def obter_dados_grafico(data_inicio=None, data_fim=None):

    conn = conectar()

    try:
        cur = conn.cursor()

        query = """
            SELECT
                DATE(data_saida),
                COUNT(*)
            FROM saidas
        """

        params = []

        if data_inicio and data_fim:
            query += """
                WHERE DATE(data_saida)
                BETWEEN %s AND %s
            """

            params.extend([data_inicio, data_fim])

        query += """
            GROUP BY DATE(data_saida)
            ORDER BY DATE(data_saida)
        """

        cur.execute(query, params)

        dados = cur.fetchall()

        datas = [str(d[0]) for d in dados]
        valores = [d[1] for d in dados]

        return datas, valores

    except Exception as e:
        logger.error(f"Erro gráfico dashboard: {e}")
        return [], []

    finally:
        conn.close()


# =====================================================
# 📈 GRÁFICO
# =====================================================
class GraficoSaidas(FigureCanvas):

    def __init__(self):

        self.fig = Figure(figsize=(5, 4))

        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111)

    def atualizar(self, data_inicio=None, data_fim=None):

        self.ax.clear()

        datas, valores = obter_dados_grafico(
            data_inicio,
            data_fim
        )

        if datas:

            self.ax.plot(
                datas,
                valores,
                marker="o"
            )

            self.ax.set_title("Saídas por Dia")
            self.ax.set_xlabel("Data")
            self.ax.set_ylabel("Quantidade")

            self.ax.grid(True)

        else:

            self.ax.text(
                0.5,
                0.5,
                "Sem dados",
                ha="center",
                va="center"
            )

        self.fig.tight_layout()

        self.draw()


# =====================================================
# 🧠 DASHBOARD
# =====================================================
class DashboardWindow(QWidget):

    def __init__(self, usuario):

        super().__init__()

        self.usuario = usuario

        self.setWindowTitle("Dashboard Executivo")
        self.resize(1200, 700)

        self.setup_ui()

        self.aplicar_filtro()

    # =================================================
    # UI
    # =================================================
    def setup_ui(self):

        layout = QHBoxLayout(self)

        # =================================================
        # MENU LATERAL
        # =================================================
        menu = QFrame()

        menu.setFixedWidth(260)

        menu.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
            }
        """)

        menu_layout = QVBoxLayout(menu)

        # =================================================
        # LOGO
        # =================================================
        logo = QLabel()

        base_dir = getattr(
            sys,
            "_MEIPASS",
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

            pixmap = QPixmap(caminho_logo)

            logo.setPixmap(
                pixmap.scaled(
                    160,
                    90,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        else:

            logo.setText("CATENA")

            logo.setStyleSheet("""
                color: white;
                font-size: 22px;
                font-weight: bold;
            """)

        logo.setAlignment(Qt.AlignCenter)

        menu_layout.addWidget(logo)

        # =================================================
        # BOTÕES
        # =================================================
        botoes = [
            ("📦 Materiais", self.abrir_materiais),
            ("🚚 Saída", self.abrir_saida),
            ("↩ Retorno", self.abrir_retorno),
            ("📜 Histórico", self.abrir_historico),
            ("💾 Backup", self.fazer_backup),
            ("📄 Exportar PDF", self.exportar_pdf),
        ]

        for texto, funcao in botoes:

            botao = QPushButton(texto)

            botao.clicked.connect(funcao)

            menu_layout.addWidget(botao)

        menu_layout.addStretch()

        layout.addWidget(menu)

        # =================================================
        # ÁREA PRINCIPAL
        # =================================================
        area = QVBoxLayout()

        # Filtros
        self.data_inicio = QDateEdit(calendarPopup=True)

        self.data_inicio.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.data_fim = QDateEdit(calendarPopup=True)

        self.data_fim.setDate(
            QDate.currentDate()
        )

        btn_atualizar = QPushButton("Atualizar")

        btn_atualizar.clicked.connect(
            self.aplicar_filtro
        )

        filtro_layout = QHBoxLayout()

        filtro_layout.addWidget(self.data_inicio)
        filtro_layout.addWidget(self.data_fim)
        filtro_layout.addWidget(btn_atualizar)

        area.addLayout(filtro_layout)

        # Gráfico
        self.grafico = GraficoSaidas()

        area.addWidget(self.grafico)

        layout.addLayout(area)

    # =================================================
    # FILTRO
    # =================================================
    def aplicar_filtro(self):

        data_inicio = self.data_inicio.date().toString(
            "yyyy-MM-dd"
        )

        data_fim = self.data_fim.date().toString(
            "yyyy-MM-dd"
        )

        if data_inicio > data_fim:

            QMessageBox.warning(
                self,
                "Erro",
                "Data inicial maior que final."
            )

            return

        self.grafico.atualizar(
            data_inicio,
            data_fim
        )

    # =================================================
    # EXPORTAR PDF
    # =================================================
    def exportar_pdf(self):

        try:
            pasta = "relatorios"

            os.makedirs(
                pasta,
                exist_ok=True
            )

            arquivo_pdf = os.path.join(
                pasta,
                f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            documento = SimpleDocTemplate(
                arquivo_pdf,
                pagesize=A4
            )

            elementos = []

            styles = getSampleStyleSheet()

            elementos.append(
                Paragraph(
                    "Relatório Executivo",
                    styles["Title"]
                )
            )

            elementos.append(
                Spacer(1, 20)
            )

            # =============================================
            # Salva gráfico temporário
            # =============================================
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png"
            ) as temp:

                caminho_temp = temp.name

            self.grafico.fig.savefig(
                caminho_temp,
                bbox_inches="tight"
            )

            elementos.append(
                Image(
                    caminho_temp,
                    width=500,
                    height=250
                )
            )

            documento.build(elementos)

            # Remove imagem temporária
            try:
                os.remove(caminho_temp)
            except Exception:
                pass

            # Abre PDF
            os.startfile(arquivo_pdf)

            logger.info(
                f"PDF gerado: {arquivo_pdf}"
            )

            QMessageBox.information(
                self,
                "Sucesso",
                f"Relatório gerado:\n{arquivo_pdf}"
            )

        except Exception as e:

            logger.error(f"Erro PDF: {e}")

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

    # =================================================
    # TELAS
    # =================================================
    def abrir_materiais(self):

        from ui.materiais import MateriaisWindow

        self.materiais_window = MateriaisWindow()

        self.materiais_window.show()

    def abrir_saida(self):

        self.saida_window = SaidaWindow(
            self.usuario
        )

        self.saida_window.show()

    def abrir_retorno(self):

        self.retorno_window = RetornoWindow()

        self.retorno_window.show()

    def abrir_historico(self):

        self.historico_window = HistoricoWindow()

        self.historico_window.show()

    # =================================================
    # BACKUP
    # =================================================
    def fazer_backup(self):

        try:

            arquivo = gerar_backup()

            QMessageBox.information(
                self,
                "Backup",
                f"Backup gerado:\n{arquivo}"
            )

            logger.info(
                f"Backup gerado: {arquivo}"
            )

        except Exception as e:

            logger.error(f"Erro backup: {e}")

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )