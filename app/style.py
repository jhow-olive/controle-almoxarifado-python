BASE_STYLE = """
* {
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 10pt;
}

/* CAMPOS */
QLineEdit,
QComboBox,
QTextEdit,
QSpinBox {
    border-radius: 10px;
    padding: 8px;
    min-height: 20px;
}

/* BOTÕES */
QPushButton {
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-weight: 600;
    min-height: 22px;
}

/* TABELAS */
QTableWidget,
QTableView {
    border-radius: 12px;
}

/* HEADER */
QHeaderView::section {
    padding: 8px;
    border: none;
    font-weight: bold;
}
"""


LIGHT_THEME = """
QWidget {
    background-color: #f8fafc;
    color: #111827;
}

QLabel {
    color: #111827;
}

QLineEdit,
QComboBox,
QTextEdit,
QSpinBox {
    background: white;
    border: 1px solid #cbd5e1;
    color: #111827;
}

QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus {
    border: 2px solid #2563eb;
}

QPushButton {
    background-color: #2563eb;
    color: white;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:pressed {
    background-color: #1e40af;
}

QPushButton:disabled {
    background-color: #94a3b8;
}

QTableWidget,
QTableView {
    background: white;
    border: 1px solid #e5e7eb;
}

QHeaderView::section {
    background-color: #e2e8f0;
    color: #111827;
}
"""


DARK_THEME = """
QWidget {
    background-color: #0f172a;
    color: #f1f5f9;
}

QLabel {
    color: #f1f5f9;
}

QLineEdit,
QComboBox,
QTextEdit,
QSpinBox {
    background: #1e293b;
    border: 1px solid #334155;
    color: #f1f5f9;
}

QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus {
    border: 2px solid #3b82f6;
}

QPushButton {
    background-color: #2563eb;
    color: white;
}

QPushButton:hover {
    background-color: #3b82f6;
}

QPushButton:pressed {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #475569;
}

QTableWidget,
QTableView {
    background: #1e293b;
    border: 1px solid #334155;
    color: #f1f5f9;
    gridline-color: #334155;
}

QHeaderView::section {
    background-color: #1e293b;
    color: #f1f5f9;
}
"""


def get_style(theme="light"):
    """
    Retorna stylesheet completo
    """

    theme = theme.lower()

    if theme == "dark":
        return BASE_STYLE + DARK_THEME

    return BASE_STYLE + LIGHT_THEME