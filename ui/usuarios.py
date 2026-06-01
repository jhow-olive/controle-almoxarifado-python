from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QFrame,
    QAbstractItemView
)

import bcrypt

from app.db import conectar


PADDING = 20


class UsuariosWindow(QWidget):

    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario

        self.setWindowTitle(
            "Usuários"
        )

        self.resize(1100, 650)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        layout.setSpacing(15)

        titulo = QLabel(
            "👥 Gerenciamento de Usuários"
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setStyleSheet("""
            font-size:20pt;
            font-weight:bold;
        """)

        layout.addWidget(titulo)

        # FORMULÁRIO
        box = QFrame()

        box.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #e5e7eb;
                border-radius:14px;
            }
        """)

        form = QHBoxLayout(box)

        form.setContentsMargins(
            PADDING,
            PADDING,
            PADDING,
            PADDING
        )

        form.setSpacing(10)

        self.txt_nome = QLineEdit()

        self.txt_nome.setPlaceholderText(
            "Nome"
        )

        self.txt_login = QLineEdit()

        self.txt_login.setPlaceholderText(
            "Login"
        )

        self.txt_senha = QLineEdit()

        self.txt_senha.setPlaceholderText(
            "Senha"
        )

        self.txt_senha.setEchoMode(
            QLineEdit.Password
        )

        self.cb_tipo = QComboBox()

        self.cb_tipo.addItems([
            "admin",
            "usuario"
        ])

        self.cb_tipo.wheelEvent = (
            lambda e: None
        )

        self.btn_salvar = QPushButton(
            "Salvar"
        )

        self.btn_salvar.setMinimumHeight(40)

        self.btn_salvar.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_salvar.clicked.connect(
            self.salvar
        )

        form.addWidget(self.txt_nome)
        form.addWidget(self.txt_login)
        form.addWidget(self.txt_senha)
        form.addWidget(self.cb_tipo)
        form.addWidget(self.btn_salvar)

        layout.addWidget(box)

        # TABELA
        self.tabela = QTableWidget()

        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels([
            "ID",
            "Nome",
            "Login",
            "Tipo",
            "Ativo"
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tabela.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tabela.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tabela.verticalHeader().setVisible(
            False
        )

        layout.addWidget(self.tabela)

        # BOTÕES
        botoes = QHBoxLayout()

        self.btn_excluir = QPushButton(
            "🗑 Excluir"
        )

        self.btn_excluir.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_excluir.clicked.connect(
            self.excluir
        )

        self.btn_atualizar = QPushButton(
            "🔄 Atualizar"
        )

        self.btn_atualizar.setCursor(
            Qt.PointingHandCursor
        )

        self.btn_atualizar.clicked.connect(
            self.carregar_dados
        )

        botoes.addWidget(
            self.btn_excluir
        )

        botoes.addWidget(
            self.btn_atualizar
        )

        botoes.addStretch()

        layout.addLayout(botoes)

        self.carregar_dados()

    def limpar_campos(self):

        self.txt_nome.clear()

        self.txt_login.clear()

        self.txt_senha.clear()

        self.cb_tipo.setCurrentIndex(0)

        self.txt_nome.setFocus()

    def carregar_dados(self):

        self.tabela.setRowCount(0)

        conn = None

        try:

            conn = conectar()

            cur = conn.cursor()

            cur.execute("""
                SELECT
                    id,
                    nome,
                    login,
                    tipo,
                    ativo
                FROM usuarios
                ORDER BY id DESC
            """)

            usuarios = cur.fetchall()

            for linha, dados in enumerate(
                usuarios
            ):

                self.tabela.insertRow(linha)

                for coluna, valor in enumerate(
                    dados
                ):

                    item = QTableWidgetItem(
                        str(valor)
                    )

                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                    self.tabela.setItem(
                        linha,
                        coluna,
                        item
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

    def salvar(self):

        nome = (
            self.txt_nome.text().strip()
        )

        login = (
            self.txt_login.text().strip()
        )

        senha = (
            self.txt_senha.text().strip()
        )

        tipo = (
            self.cb_tipo.currentText()
        )

        if (
            not nome
            or not login
            or not senha
        ):

            QMessageBox.warning(
                self,
                "Erro",
                "Preencha todos os campos."
            )

            return

        try:

            self.btn_salvar.setEnabled(
                False
            )

            senha_hash = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            conn = conectar()

            cur = conn.cursor()

            # VERIFICA LOGIN
            cur.execute("""
                SELECT id
                FROM usuarios
                WHERE login = %s
            """, (login,))

            existe = cur.fetchone()

            if existe:

                QMessageBox.warning(
                    self,
                    "Erro",
                    "Login já existe."
                )

                return

            cur.execute("""
                INSERT INTO usuarios (
                    nome,
                    login,
                    senha,
                    tipo,
                    ativo
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    1
                )
            """, (
                nome,
                login,
                senha_hash,
                tipo
            ))

            conn.commit()

            QMessageBox.information(
                self,
                "Sucesso",
                "Usuário cadastrado!"
            )

            self.limpar_campos()

            self.carregar_dados()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

        finally:

            try:
                conn.close()
            except Exception:
                pass

            self.btn_salvar.setEnabled(
                True
            )

    def excluir(self):

        linha = self.tabela.currentRow()

        if linha < 0:

            QMessageBox.warning(
                self,
                "Erro",
                "Selecione um usuário."
            )

            return

        user_id = self.tabela.item(
            linha,
            0
        ).text()

        nome = self.tabela.item(
            linha,
            1
        ).text()

        resposta = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            (
                f"Deseja excluir "
                f"o usuário '{nome}'?"
            )
        )

        if (
            resposta
            != QMessageBox.StandardButton.Yes
        ):
            return

        conn = None

        try:

            conn = conectar()

            cur = conn.cursor()

            cur.execute("""
                DELETE FROM usuarios
                WHERE id = %s
            """, (user_id,))

            conn.commit()

            QMessageBox.information(
                self,
                "Sucesso",
                "Usuário excluído!"
            )

            self.carregar_dados()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Erro",
                str(e)
            )

        finally:

            if conn:
                conn.close()