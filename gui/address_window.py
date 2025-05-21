import sqlite3
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QLabel, QMessageBox
)
from style import apply_button_style
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import sys
class AddressWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Реестр адресов")
        self.resize(300, 400)

        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
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
        self.input_field = QLineEdit()
        self.add_button = QPushButton("Добавить")
        self.remove_button = QPushButton("Удалить выбранные")

        layout.addWidget(QLabel("Адреса:"))
        layout.addWidget(self.list_widget)
        layout.addWidget(self.input_field)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico")))
        apply_button_style(self.add_button, self.remove_button)

        self.setLayout(layout)
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        self._conn = sqlite3.connect(db_path)

        self.refresh()
        self.add_button.clicked.connect(self.add_admin)
        self.remove_button.clicked.connect(self.remove_selected)

    def refresh(self):
        self.list_widget.clear()
        cur = self._conn.cursor()
        cur.execute("SELECT address FROM addresses")
        for row in cur.fetchall():
            item = QListWidgetItem(row[0])
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

    def add_admin(self):
        name = self.input_field.text().strip()
        if not name:
            return

        try:
            cur = self._conn.cursor()
            cur.execute("SELECT COUNT(*) FROM addresses WHERE LOWER(address) = LOWER(?)", (name.lower(),))
            if cur.fetchone()[0] > 0:
                QMessageBox.warning(self, "Ошибка", f"Адрес '{name}' уже есть в базе данных.")
                return

            cur.execute("INSERT INTO addresses (address) VALUES (?)", (name,))
            self._conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
            return

        self.input_field.clear()
        self.refresh()

    def remove_selected(self):
        items_to_remove = [self.list_widget.item(i) for i in range(self.list_widget.count()) if self.list_widget.item(i).checkState() == Qt.CheckState.Checked]
        if not items_to_remove:
            QMessageBox.information(self, "Нет выбора", "Выберите хотя бы одного администратора для удаления.")
            return

        cur = self._conn.cursor()
        for item in items_to_remove:
            cur.execute("DELETE FROM addresses WHERE address=?", (item.text(),))
        self._conn.commit()
        self.refresh()
