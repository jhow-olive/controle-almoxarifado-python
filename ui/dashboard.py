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
    QDateEdit,
    QSizePolicy
)

from PySide6.QtGui import QPixmap, Qt
from PySide6.QtCore import QDate

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

        self.fig = Figure(
            figsize=(5, 4),
            facecolor="#111827"
        )

        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111)

    def atualizar(self, data_inicio=None, data_fim=None):

        self.ax.clear()

        # Tema Dark
        self.ax.set_facecolor("#1F2937")

        self.ax.tick_params(colors="white")

        self.ax.title.set_color("white")

        self.ax.xaxis.label.set_color("white")

        self.ax.yaxis.label.set_color("white")

        for spine in self.ax.spines.values():
            spine.set_color("#374151")

        datas, valores = obter_dados_grafico(
            data_inicio,
            data_fim
        )

        if datas:

            self.ax.plot(
                datas,
                valores,
                marker="o",
                linewidth=3
            )

            self.ax.set_title(
                "Saídas por Dia",
                fontsize=14
            )

            self.ax.set_xlabel("Data")

            self.ax.set_ylabel("Quantidade")

            self.ax.grid(
                True,
                linestyle="--",
                alpha=0.3
            )

        else:

            self.ax.text(
                0.5,
                0.5,
                "Sem dados",
                ha="center",
                va="center",
                color="white",
                fontsize=16
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

        self.setWindowTitle(
            "Dashboard Executivo"
        )

        self.resize(1400, 800)

        self.setup_ui()

        self.aplicar_estilo()

        self.aplicar_filtro()

    # =================================================
    # 🎨 ESTILO
    # =================================================
    def aplicar_estilo(self):

        self.setStyleSheet("""
            QWidget {
                background-color: #111827;
                color: #F3F4F6;
                font-family: Segoe UI;
                font-size: 14px;
            }

            QLabel {
                color: #F9FAFB;
            }

            QPushButton {
                background-color: #2563EB;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-weight: bold;
                color: white;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:pressed {
                background-color: #1E40AF;
            }

            QDateEdit {
                background-color: #374151;
                border: 1px solid #4B5563;
                border-radius: 10px;
                padding: 8px;
                color: white;
            }

            QMessageBox {
                background-color: #1F2937;
            }
        """)

    # =================================================
    # 🖥 UI
    # =================================================
    def setup_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        # =================================================
        # MENU LATERAL
        # =================================================
        menu = QFrame()

        menu.setFixedWidth(260)

        menu.setStyleSheet("""
            QFrame {
                background-color: #0B1120;
                border-right: 1px solid #1F2937;
            }
        """)

        menu_layout = QVBoxLayout(menu)

        menu_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        menu_layout.setSpacing(10)

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
                    180,
                    100,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        else:

            logo.setText("CATENA")

            logo.setStyleSheet("""
                color: #2563EB;
                font-size: 26px;
                font-weight: bold;
            """)

        logo.setAlignment(Qt.AlignCenter)

        menu_layout.addWidget(logo)

        menu_layout.addSpacing(30)

        # =================================================
        # BOTÕES MENU
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

            botao.setCursor(
                Qt.PointingHandCursor
            )

            botao.clicked.connect(funcao)

            botao.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    text-align: left;
                    padding: 14px;
                    border-radius: 12px;
                    font-size: 15px;
                    color: white;
                }

                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)

            menu_layout.addWidget(botao)

        menu_layout.addStretch()

        # =================================================
        # USUÁRIO
        # =================================================
        usuario_label = QLabel(
            f"Usuário: {self.usuario}"
        )

        usuario_label.setStyleSheet("""
            color: #9CA3AF;
            padding: 10px;
            font-size: 13px;
        """)

        menu_layout.addWidget(usuario_label)

        layout.addWidget(menu)

        # =================================================
        # ÁREA PRINCIPAL
        # =================================================
        area_widget = QWidget()

        area = QVBoxLayout(area_widget)

        area.setContentsMargins(
            30,
            30,
            30,
            30
        )

        area.setSpacing(20)

        # =================================================
        # TÍTULO
        # =================================================
        titulo = QLabel("Dashboard Executivo")

        titulo.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        subtitulo = QLabel(
            "Visão geral do almoxarifado"
        )

        subtitulo.setStyleSheet("""
            color: #9CA3AF;
            font-size: 14px;
        """)

        area.addWidget(titulo)
        area.addWidget(subtitulo)

        # =================================================
        # CARDS
        # =================================================
        cards_layout = QHBoxLayout()

        cards = [
            ("📦 Materiais", "245"),
            ("🚚 Em Uso", "38"),
            ("⚠ Pendências", "12"),
            ("👤 Usuários", "7")
        ]

        for titulo_card, valor in cards:

            card = QFrame()

            card.setMinimumHeight(140)

            card.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            card.setStyleSheet("""
                QFrame {
                    background-color: #1F2937;
                    border-radius: 20px;
                    padding: 15px;
                }

                QFrame:hover {
                    border: 2px solid #2563EB;
                }
            """)

            card_layout = QVBoxLayout(card)

            titulo_label = QLabel(titulo_card)

            titulo_label.setStyleSheet("""
                font-size: 14px;
                color: #9CA3AF;
            """)

            valor_label = QLabel(valor)

            valor_label.setStyleSheet("""
                font-size: 32px;
                font-weight: bold;
                color: #2563EB;
            """)

            card_layout.addWidget(titulo_label)
            card_layout.addSpacing(10)
            card_layout.addWidget(valor_label)

            cards_layout.addWidget(card)

        area.addLayout(cards_layout)

        # =================================================
        # FILTROS
        # =================================================
        filtro_frame = QFrame()

        filtro_frame.setStyleSheet("""
            QFrame {
                background-color: #1F2937;
                border-radius: 18px;
                padding: 10px;
            }
        """)

        filtro_layout = QHBoxLayout(filtro_frame)

        self.data_inicio = QDateEdit(
            calendarPopup=True
        )

        self.data_inicio.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.data_fim = QDateEdit(
            calendarPopup=True
        )

        self.data_fim.setDate(
            QDate.currentDate()
        )

        btn_atualizar = QPushButton(
            "Atualizar"
        )

        btn_atualizar.clicked.connect(
            self.aplicar_filtro
        )

        filtro_layout.addWidget(
            QLabel("Data Inicial")
        )

        filtro_layout.addWidget(
            self.data_inicio
        )

        filtro_layout.addSpacing(10)

        filtro_layout.addWidget(
            QLabel("Data Final")
        )

        filtro_layout.addWidget(
            self.data_fim
        )

        filtro_layout.addSpacing(20)

        filtro_layout.addWidget(
            btn_atualizar
        )

        filtro_layout.addStretch()

        area.addWidget(filtro_frame)

        # =================================================
        # GRÁFICO
        # =================================================
        grafico_frame = QFrame()

        grafico_frame.setStyleSheet("""
            QFrame {
                background-color: #1F2937;
                border-radius: 20px;
                padding: 20px;
            }
        """)

        grafico_layout = QVBoxLayout(
            grafico_frame
        )

        self.grafico = GraficoSaidas()

        grafico_layout.addWidget(
            self.grafico
        )

        area.addWidget(grafico_frame)

        layout.addWidget(area_widget)

    # =================================================
    # 🔍 FILTRO
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
    # 📄 EXPORTAR PDF
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

            try:
                os.remove(caminho_temp)
            except Exception:
                pass

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

            logger.error(
                f"Erro PDF: {e}"
            )

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

    # =================================================
    # 🪟 TELAS
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
    # 💾 BACKUP
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

            logger.error(
                f"Erro backup: {e}"
            )

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )