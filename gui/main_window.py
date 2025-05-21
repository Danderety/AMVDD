import os
import sqlite3
import platform
from PyQt6.QtGui import QIcon

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMenu, QMessageBox, QCheckBox, QStyle, QStyledItemDelegate,
    QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, QPoint, QTimer
from gui.computer_form import ComputerForm
from gui.dst_window import DstMainWindow
from gui.address_window import AddressWindow
from gui.admin_window import AdminWindow
from style import apply_button_style
from utils.hardware_utils import get_ip_info
from gui.export_report import generate_report_to_excel
import sys
class CenteredCheckBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        return None

class MainWindow(QWidget):
    def __init__(self, theme=None, save_theme=None, apply_theme=None):
        super().__init__()
        self.theme = theme
        self.save_theme = save_theme
        self.apply_theme = apply_theme

        self.setWindowTitle("Реестр компьютеров")
        self.resize(900, 500)
        
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico")))
        root_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        self.sidebar_layout = QVBoxLayout()
        for label, callback in [
            ("ДСТ", self.open_dst_window),
            ("Адреса", self.open_address_window),
            ("Администраторы", self.open_admin_window)
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(callback)
            apply_button_style(btn)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()
        self.settings_button = QPushButton()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.settings_button.setIcon(icon)
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.open_settings_menu)
        apply_button_style(self.settings_button)
        self.sidebar_layout.addWidget(self.settings_button)

        top_layout.addLayout(self.sidebar_layout)

        right_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени...")
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_input)
        right_layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["", "Имя компьютера", "IP-адрес"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_context_menu)
        self.table.itemDoubleClicked.connect(self.edit_selected_computer)
        self.table.setItemDelegateForColumn(0, CenteredCheckBoxDelegate())
        self.table.setSortingEnabled(True)
        right_layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить компьютер")
        self.add_button.clicked.connect(self.add_computer)
        apply_button_style(self.add_button)

        self.report_button = QPushButton("Сформировать отчет")
        self.report_button.clicked.connect(self.generate_report)
        apply_button_style(self.report_button)
        self.report_button.setVisible(False)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.report_button)
        right_layout.addLayout(buttons_layout)

        top_layout.addLayout(right_layout)
        root_layout.addLayout(top_layout)
        self.setLayout(root_layout)

        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        search_term = self.search_input.text().lower().strip() if hasattr(self, 'search_input') else ""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        
        cur = conn.cursor()
        cur.execute("SELECT id, name, ip FROM computers ORDER BY name COLLATE NOCASE")
        results = cur.fetchall()
        conn.close()

        self.computer_ids = []
        for row_data in results:
            if search_term and search_term not in row_data[1].lower():
                continue
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            self.computer_ids.append(row_data[0])

            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    margin: auto;
                }
                QCheckBox::indicator:checked {
                    background-color: #2a82da;
                }
            """)
            self.table.setCellWidget(row_num, 0, checkbox)

            name_item = QTableWidgetItem(str(row_data[1]))
            ip_item = QTableWidgetItem(str(row_data[2]))
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            ip_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row_num, 1, name_item)
            self.table.setItem(row_num, 2, ip_item)

        self.report_button.setVisible(len(self.computer_ids) > 0)

    def get_selected_ids(self):
        ids = []
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox.isChecked():
                ids.append(self.computer_ids[row])
        return ids

    def open_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        if self.theme == "dark":
            menu.setStyleSheet("QMenu { background-color: #333; color: white; }")
        else:
            menu.setStyleSheet("QMenu { background-color: #fff; color: black; }")

        ids = self.get_selected_ids()
        if len(ids) == 1:
            menu.addAction("Удалить компьютер", lambda: self.delete_ids(ids))
        elif len(ids) > 1:
            menu.addAction("Удалить компьютеры", lambda: self.delete_ids(ids))
        if not menu.isEmpty():
            menu.exec(self.table.mapToGlobal(pos))

    def delete_ids(self, ids):
        if not ids:
            return
        confirm = QMessageBox.question(
            self, "Удаление", f"Удалить {len(ids)} компьютеров?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        
        cur = conn.cursor()
        for computer_id in ids:
            cur.execute("DELETE FROM computers WHERE id = ?", (computer_id,))
            cur.execute("DELETE FROM disks WHERE computer_id = ?", (computer_id,))
            cur.execute("DELETE FROM network_interfaces WHERE computer_id = ?", (computer_id,))
        conn.commit()
        conn.close()
        self.load_data()

    def open_settings_menu(self):
        menu = QMenu()
        if self.theme == "dark":
            menu.setStyleSheet("QMenu { background-color: #333; color: white; }")
        else:
            menu.setStyleSheet("QMenu { background-color: #fff; color: black; }")

        theme_menu = menu.addMenu("Тема")
        theme_menu.addAction("Светлая", lambda: self.change_theme("light"))
        theme_menu.addAction("Тёмная", lambda: self.change_theme("dark"))
        menu.exec(self.settings_button.mapToGlobal(QPoint(0, self.settings_button.height())))

    def change_theme(self, theme_name):
        if self.apply_theme and self.save_theme:
            self.theme = theme_name
            self.apply_theme(theme_name)
            self.save_theme(theme_name)
            self.load_data()

    def add_computer(self):
        name = platform.node()
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM computers WHERE name = ?", (name,))
        existing = cur.fetchone()
        conn.close()

        if existing:
            QMessageBox.warning(self, "Внимание", "Такой компьютер уже существует.")
            return

        form = ComputerForm()
        form.save_data()
       
        self.load_data()

    def edit_selected_computer(self, item):
        row = item.row()
        if row < len(self.computer_ids):
            self.form = ComputerForm(computer_id=self.computer_ids[row])
            self.form.show()
            self.form.destroyed.connect(self.load_data)

    def generate_report(self):
        generate_report_to_excel()

    def open_dst_window(self):
        self.dst_win = DstMainWindow()
        self.dst_win.show()

    def open_address_window(self):
        self.addr_win = AddressWindow()
        self.addr_win.show()

    def reload_computers(self):
        print("[DEBUG] Обновление списка компьютеров...")
        self.load_data()

    def open_admin_window(self):
        self.admin_win = AdminWindow()
        self.admin_win.show()
