BASE_STYLE = """
* {
    font-family: Segoe UI;
    font-size: 10pt;
}


/* =====================================================
   WIDGETS GERAIS
===================================================== */

QWidget {
    selection-background-color: #2563EB;
    selection-color: white;
}


/* =====================================================
   LABELS
===================================================== */

QLabel {
    background: transparent;
}


/* =====================================================
   INPUTS
===================================================== */

QLineEdit,
QComboBox,
QTextEdit,
QSpinBox,
QDateEdit {
    border-radius: 14px;
    padding: 10px;
    min-height: 22px;
    border: 1px solid;
    font-size: 10pt;
}


/* =====================================================
   BOTÕES
===================================================== */

QPushButton {
    border: none;
    border-radius: 14px;
    padding: 12px 16px;
    font-weight: 600;
    min-height: 24px;
}


QPushButton:hover {
    transition: 0.3s;
}


/* =====================================================
   TABELAS
===================================================== */

QTableWidget,
QTableView {
    border-radius: 16px;
    border: 1px solid;
    gridline-color: transparent;
    padding: 6px;
}


QTableWidget::item,
QTableView::item {
    padding: 8px;
}


QTableWidget::item:selected,
QTableView::item:selected {
    background-color: #2563EB;
    color: white;
}


/* =====================================================
   HEADER
===================================================== */

QHeaderView::section {
    padding: 12px;
    border: none;
    font-weight: bold;
    font-size: 10pt;
}


/* =====================================================
   SCROLLBAR
===================================================== */

QScrollBar:vertical {
    border: none;
    width: 10px;
    margin: 0px;
}


QScrollBar::handle:vertical {
    border-radius: 5px;
    min-height: 20px;
}


QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}


QScrollBar:horizontal {
    border: none;
    height: 10px;
    margin: 0px;
}


QScrollBar::handle:horizontal {
    border-radius: 5px;
    min-width: 20px;
}


QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}


/* =====================================================
   COMBOBOX
===================================================== */

QComboBox {
    padding-right: 25px;
}


QComboBox::drop-down {
    border: none;
    width: 24px;
}


/* =====================================================
   TOOLTIP
===================================================== */

QToolTip {
    border-radius: 10px;
    padding: 8px;
    font-size: 10pt;
}


/* =====================================================
   MENU
===================================================== */

QMenu {
    border-radius: 12px;
    padding: 8px;
}


QMenu::item {
    padding: 10px 20px;
    border-radius: 8px;
}


QMenu::item:selected {
    background-color: #2563EB;
    color: white;
}
"""


# =====================================================
# LIGHT THEME
# =====================================================
LIGHT_THEME = """
QWidget {
    background-color: #F8FAFC;
    color: #111827;
}


/* INPUTS */

QLineEdit,
QComboBox,
QTextEdit,
QSpinBox,
QDateEdit {
    background: white;
    border-color: #CBD5E1;
    color: #111827;
}


QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus,
QDateEdit:focus {
    border: 2px solid #2563EB;
}


/* BOTÕES */

QPushButton {
    background-color: #2563EB;
    color: white;
}


QPushButton:hover {
    background-color: #1D4ED8;
}


QPushButton:pressed {
    background-color: #1E40AF;
}


QPushButton:disabled {
    background-color: #94A3B8;
}


/* TABELAS */

QTableWidget,
QTableView {
    background: white;
    border-color: #E5E7EB;
}


QHeaderView::section {
    background-color: #E2E8F0;
    color: #111827;
}


/* SCROLLBAR */

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #E5E7EB;
}


QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #94A3B8;
}


/* TOOLTIP */

QToolTip {
    background-color: white;
    color: #111827;
    border: 1px solid #CBD5E1;
}


/* MENU */

QMenu {
    background-color: white;
    border: 1px solid #CBD5E1;
    color: #111827;
}
"""


# =====================================================
# DARK THEME
# =====================================================
DARK_THEME = """
QWidget {
    background-color: #0F172A;
    color: #F1F5F9;
}


/* INPUTS */

QLineEdit,
QComboBox,
QTextEdit,
QSpinBox,
QDateEdit {
    background: #1E293B;
    border-color: #334155;
    color: #F1F5F9;
}


QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus,
QDateEdit:focus {
    border: 2px solid #3B82F6;
}


/* BOTÕES */

QPushButton {
    background-color: #2563EB;
    color: white;
}


QPushButton:hover {
    background-color: #3B82F6;
}


QPushButton:pressed {
    background-color: #1D4ED8;
}


QPushButton:disabled {
    background-color: #475569;
}


/* TABELAS */

QTableWidget,
QTableView {
    background: #1E293B;
    border-color: #334155;
    color: #F1F5F9;
    gridline-color: #334155;
}


QHeaderView::section {
    background-color: #1E293B;
    color: #F1F5F9;
}


/* SCROLLBAR */

QScrollBar:vertical,
QScrollBar:horizontal {
    background: #111827;
}


QScrollBar::handle:vertical,
QScrollBar::handle:horizontal {
    background: #475569;
}


/* TOOLTIP */

QToolTip {
    background-color: #1E293B;
    color: white;
    border: 1px solid #334155;
}


/* MENU */

QMenu {
    background-color: #1E293B;
    border: 1px solid #334155;
    color: white;
}
"""


# =====================================================
# GET STYLE
# =====================================================
def get_style(theme="dark"):
    """
    Retorna stylesheet completo
    """

    theme = theme.lower()

    if theme == "light":
        return BASE_STYLE + LIGHT_THEME

    return BASE_STYLE + DARK_THEME