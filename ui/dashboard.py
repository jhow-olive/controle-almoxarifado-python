import os
import sys
import tempfile
import subprocess
import platform
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
    QGridLayout
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

def obter_indicadores():

    indicadores = {
        "materiais": 0,
        "em_uso": 0,
        "usuarios": 0,
        "veiculos": 0
    }

    conn = conectar()

    try:

        cur = conn.cursor()

        # Total materiais cadastrados
        cur.execute("""
            SELECT COUNT(*)
            FROM materiais
        """)

        indicadores["materiais"] = cur.fetchone()[0]

        # Saídas abertas
        cur.execute("""
            SELECT COUNT(*)
            FROM saidas
            WHERE status = 'ABERTO'
        """)

        indicadores["em_uso"] = cur.fetchone()[0]

        # Usuários ativos
        cur.execute("""
            SELECT COUNT(*)
            FROM usuarios
            WHERE ativo = 1
        """)

        indicadores["usuarios"] = cur.fetchone()[0]

        # Veículos cadastrados
        cur.execute("""
            SELECT COUNT(*)
            FROM veiculos
        """)

        indicadores["veiculos"] = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM saida_itens
            WHERE quantidade > retornado
        """)

        indicadores["pendencias"] = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM materiais
            WHERE quantidade_disponivel <= COALESCE(estoque_minimo,5)
        """)

        indicadores["criticos"] = cur.fetchone()[0]

    except Exception as e:

        logger.error(
            f"Erro indicadores: {e}"
        )

    finally:

        conn.close()

    return indicadores


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
                linewidth=3,
                color="#3B82F6"
            )

            self.ax.fill_between(
                datas,
                valores,
                alpha=0.2,
                color="#3B82F6"
            )

            self.ax.set_xlabel("Data")

            self.ax.set_ylabel("Quantidade")

            self.ax.set_title(
                "Saídas por Dia",
                color="white",
                fontsize=14
            )

            self.ax.tick_params(
                axis="x",
                rotation=45
            )

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

        self.fig.tight_layout(pad=3)

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

        self.atualizar_dashboard()

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
                background-color: transparent;
                text-align: left;
                padding: 16px;
                border-radius: 14px;
                font-size: 15px;
                color: #E2E8F0;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1E293B;
                border-left: 4px solid #3B82F6;
            }

            QPushButton:pressed {
                background-color: #2563EB;
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
            ("🚗 Veículos", self.abrir_veiculos),
            ("👥 Usuários", self.abrir_usuarios),
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
        nome_usuario = (
            self.usuario["nome"]
            if isinstance(self.usuario, dict)
            else str(self.usuario)
        )

        usuario_topo = QLabel(
            f"👤 {nome_usuario}"
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
        # TOPBAR
        # =================================================
        topbar = QFrame()

        topbar.setFixedHeight(70)

        topbar.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border-radius: 18px;
            }
        """)

        topbar_layout = QHBoxLayout(topbar)

        titulo_topo = QLabel("Bem-vindo ao Sistema")

        titulo_topo.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        usuario_label = QLabel(
            f"Usuário: {nome_usuario}"
        )

        usuario_topo.setStyleSheet("""
            color: #94A3B8;
            font-size: 14px;
        """)

        topbar_layout.addWidget(titulo_topo)

        topbar_layout.addStretch()

        topbar_layout.addWidget(usuario_topo)

        area.addWidget(topbar)

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
        # CARDS PREMIUM
        # =================================================
        indicadores = obter_indicadores()

        card1, self.lbl_materiais = self.criar_card(
            "📦 Materiais",
            indicadores["materiais"],
            "#3B82F6"
        )
        
                
        card2, self.lbl_em_uso = self.criar_card(
            "🚚 Saídas Abertas",
            indicadores["em_uso"],
            "#10B981"
        )

        card3, self.lbl_pendencias = self.criar_card(
            "⚠ Pendências",
            indicadores["pendencias"],
            "#F59E0B"
        )

        card4, self.lbl_veiculos = self.criar_card(
            "🚗 Veículos",
            indicadores["veiculos"],
            "#EF4444"
        )

        card5, self.lbl_usuarios = self.criar_card(
            "👥 Usuários",
            indicadores["usuarios"],
            "#8B5CF6"
        )

        card6, self.lbl_criticos = self.criar_card(
            "⚠ Estoque Crítico",
            indicadores["criticos"],
            "#DC2626"
        )
    

        cards_layout = QGridLayout()
        
        cards_layout.setHorizontalSpacing(20)
        cards_layout.setVerticalSpacing(20)

        cards_layout.addWidget(card1, 0, 0)
        cards_layout.addWidget(card2, 0, 1)
        cards_layout.addWidget(card3, 0, 2)

        cards_layout.addWidget(card4, 1, 0)
        cards_layout.addWidget(card5, 1, 1)
        cards_layout.addWidget(card6, 1, 2)

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
            QDate.currentDate().addMonths(-6)
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

        self.grafico.setMinimumHeight(450)

        grafico_layout.addWidget(
            self.grafico
        )


        area.addWidget(grafico_frame)

        layout.addWidget(area_widget)

    # =================================================
    # 🎴 CARD PREMIUM
    # =================================================
    def criar_card(self, titulo, valor, cor="#2563EB"):

        card = QFrame()

        card.setMinimumHeight(150)

        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E293B;
                border-radius: 22px;
                border: 1px solid #334155;
            }}

            QFrame:hover {{
                border: 2px solid {cor};
            }}
        """)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(20, 20, 20, 20)

        titulo_label = QLabel(titulo)

        titulo_label.setStyleSheet("""
            color: #94A3B8;
            font-size: 14px;
            font-weight: 500;
        """)

        valor_label = QLabel(str(valor))

        valor_label.setStyleSheet(f"""
            color: {cor};
            font-size: 38px;
            font-weight: bold;
        """)

        linha = QFrame()

        linha.setFixedHeight(4)

        linha.setStyleSheet(f"""
            background-color: {cor};
            border-radius: 2px;
        """)

        layout.addWidget(titulo_label)

        layout.addSpacing(10)

        layout.addWidget(valor_label)

        layout.addStretch()

        layout.addWidget(linha)

        return card, valor_label

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

            elementos.append(Spacer(1,20))

            indicadores = obter_indicadores()

            elementos.append(
                Paragraph(
                    f"""
                    <b>Materiais:</b> {indicadores['materiais']}<br/>
                    <b>Saídas abertas:</b> {indicadores['em_uso']}<br/>
                    <b>Pendências:</b> {indicadores['pendencias']}<br/>
                    <b>Usuários:</b> {indicadores['usuarios']}<br/>
                    <b>Veículos:</b> {indicadores['veiculos']}<br/>
                    <b>Estoque crítico:</b> {indicadores['criticos']}
                    """,
                    styles["BodyText"]
                )
            )

            elementos.append(Spacer(1,20))

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

            if platform.system() == "Windows":
                os.startfile(arquivo_pdf)

            elif platform.system() == "Darwin":
                subprocess.Popen(["open", arquivo_pdf])

            else:
                subprocess.Popen(["xdg-open", arquivo_pdf])

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

        self.materiais_window = MateriaisWindow(self.usuario)

        self.materiais_window.show()

        self.materiais_window.destroyed.connect(
            self.atualizar_dashboard
        )

    def abrir_saida(self):

        self.saida_window = SaidaWindow(
            self.usuario
        )

        self.saida_window.show()

        self.saida_window.destroyed.connect(
            lambda: (
                self.atualizar_dashboard(),
                self.aplicar_filtro()
            )
        )

    def abrir_retorno(self):

        self.retorno_window = SaidaWindow(
            self.usuario
        )

        self.retorno_window.show()

        self.retorno_window.destroyed.connect(
            self.atualizar_dashboard
        )

    def abrir_historico(self):

        self.historico_window = SaidaWindow(
            self.usuario
        )

        self.historico_window.show()

        self.historico_window.destroyed.connect(
            self.atualizar_dashboard
        )

    def abrir_usuarios(self):
        from ui.usuarios import UsuariosWindow

        self.usuarios_window = SaidaWindow(
            self.usuario
        )

        self.usuarios_window.show()

        self.usuarios_window.destroyed.connect(
            self.atualizar_dashboard
        )

    def abrir_veiculos(self):
        from ui.veiculos import VeiculosWindow

        self.veiculo_window = SaidaWindow(
            self.usuario
        )

        self.veiculo_window.show()

        self.veiculo_window.destroyed.connect(
            self.atualizar_dashboard
        )

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

    def atualizar_dashboard(self):

        indicadores = obter_indicadores()

        if hasattr(self, "lbl_materiais"):
            self.lbl_materiais.setText(
                str(indicadores["materiais"])
        )

        if hasattr(self, "lbl_em_uso"):
            self.lbl_em_uso.setText(
                str(indicadores["em_uso"])
        )

        if hasattr(self, "lbl_pendencias"):
            self.lbl_pendencias.setText(
                str(indicadores["pendencias"])
        )

        if hasattr(self, "lbl_veiculos"):
            self.lbl_veiculos.setText(
                str(indicadores["veiculos"])
        )

        if hasattr(self, "lbl_usuarios"):
            self.lbl_usuarios.setText(
                str(indicadores["usuarios"])
            )

        if hasattr(self, "lbl_criticos"):
            self.lbl_criticos.setText(
                str(indicadores["criticos"])
            )
      