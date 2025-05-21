import os
import winreg
import sqlite3
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from style import apply_button_style

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QApplication, QInputDialog, QMainWindow, QMenu
)
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QDialog

from PyQt6.QtGui import QFont

from PyQt6.QtGui import QIcon

class DstFinder(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Поиск ДСТ")
        
        self.setStyleSheet("""
            QDialog {
                background-color: palette(window);
                color: palette(window-text);
            }
            QListWidget {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid gray;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QMessageBox {
                background-color: palette(window);
                color: palette(window-text);
            }
            QInputDialog {
                background-color: palette(window);
                color: palette(window-text);
            }
        """)
        self.setFont(QFont("Segoe UI", 10))
        self.layout = QVBoxLayout(self)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico")))
        self.find_button = QPushButton("Найти ДСТ автоматически")
        apply_button_style(self.find_button)
        self.find_button.clicked.connect(self.find_dst)
        self.layout.addWidget(self.find_button)

        self.result_list = QListWidget()
        self.result_list.setFont(QFont("Segoe UI", 10))
        self.result_list.setStyleSheet("""
            QListWidget {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid gray;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self.layout.addWidget(self.result_list)

        self.add_button = QPushButton("Добавить выбранные в базу данных")
        apply_button_style(self.add_button)
        self.add_button.clicked.connect(self.add_selected_to_db)
        self.layout.addWidget(self.add_button)

    def find_dst(self):
        base_path = r"SOFTWARE\WOW6432Node\InfoTecS\ITCSShared\Logon"
        found_users = []

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_path) as base_key:
                for i in range(0, winreg.QueryInfoKey(base_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(base_key, i)
                        full_path = f"{base_path}\\{subkey_name}"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, full_path) as sub_key:
                            try:
                                name, _ = winreg.QueryValueEx(sub_key, "LastLoggedInUserName")
                                found_users.append(name)
                            except FileNotFoundError:
                                continue
                    except OSError:
                        continue
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", "Раздел реестра не найден.")

        if not found_users:
            manual, ok = QInputDialog.getText(self, "Ввод вручную", "Не удалось найти ДСТ автоматически.\nВведите значения вручную через запятую:")
            if ok and manual.strip():
                found_users = [x.strip() for x in manual.split(",") if x.strip()]
            else:
                return

        self.result_list.clear()
        for user in found_users:
            item = QListWidgetItem(str(user))
            item.setCheckState(Qt.CheckState.Unchecked)
            self.result_list.addItem(item)

    def add_selected_to_db(self):
        selected = [
            self.result_list.item(i).text()
            for i in range(self.result_list.count())
            if self.result_list.item(i).checkState() == Qt.CheckState.Checked
        ]

        if not selected:
            QMessageBox.information(self, "Ничего не выбрано", "Пожалуйста, выберите хотя бы одну запись.")
            return

        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS dst (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)

        existing_names = set(row[0] for row in cur.execute("SELECT name FROM dst"))

        for name in selected:
            if name in existing_names:
                QMessageBox.warning(self, "Повтор", f"Запись '{name}' уже существует в базе данных.")
                continue
            try:
                cur.execute("INSERT OR IGNORE INTO dst (name) VALUES (?)", (name,))
                
            except Exception as e:
                print(f"Ошибка при добавлении '{name}': {e}")

        conn.commit()
        conn.close()
        
        if hasattr(self.parent(), 'load_dst'):
            self.parent().load_dst()

class DstMainWindow(QMainWindow):
    

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление ДСТ")
        self.resize(300, 400)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico")))
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.dst_list = QListWidget()
        self.dst_list.setFont(QFont("Segoe UI", 10))
        self.dst_list.setStyleSheet("""
            QListWidget {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid gray;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        self.dst_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.dst_list.customContextMenuRequested.connect(self.open_context_menu)
        layout.addWidget(self.dst_list)
        
        open_dst_finder_button = QPushButton("Добавить ДСТ")
        apply_button_style(open_dst_finder_button)
        open_dst_finder_button.clicked.connect(self.open_dst_finder)
        layout.addWidget(open_dst_finder_button)

        self.load_dst()

    def open_context_menu(self, position):
        menu = QMenu()
        delete_action = menu.addAction("Удалить ДСТ")
        action = menu.exec(self.dst_list.viewport().mapToGlobal(position))
        if action == delete_action:
            self.delete_selected_dst()

    def delete_selected_dst(self):
        selected_items = [self.dst_list.item(i) for i in range(self.dst_list.count()) if self.dst_list.item(i).checkState() == Qt.CheckState.Checked]
        if not selected_items:
            QMessageBox.information(self, "Нет выбора", "Выберите хотя бы один элемент для удаления.")
            return

        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        for item in selected_items:
            name = item.text()
            cur.execute("DELETE FROM dst WHERE name = ?", (name,))

        conn.commit()
        conn.close()
        self.load_dst()

    def load_dst(self):
        self.dst_list.clear()
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS dst (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
        cur.execute("SELECT name FROM dst")
        for row in cur.fetchall():
            item = QListWidgetItem(row[0])
            item.setCheckState(Qt.CheckState.Unchecked)
            self.dst_list.addItem(item)

        conn.close()

    def open_dst_finder(self):
        self.dst_finder = DstFinder()
        self.dst_finder.exec()
        self.load_dst()


