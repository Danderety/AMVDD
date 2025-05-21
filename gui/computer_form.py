import sqlite3
import platform
import os 
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QComboBox, QHeaderView
)
from PyQt6.QtGui import QIcon
import sys
from PyQt6.QtCore import Qt
from style import apply_button_style
from utils.hardware_utils import get_disks, get_ip_info, get_os_info

class ComputerForm(QWidget):
    def __init__(self, computer_id=None):
        super().__init__()
        self.setWindowTitle("Информация о компьютере")
        self.resize(600, 500)

        self.computer_id = computer_id
        self.data = {}
        self.widgets = {}
        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Группа", "Атрибут", "Значение"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_data)
        apply_button_style(self.save_button)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "icons", "icon.ico")))
        if self.computer_id:
            self.prepare_data()
            self.fill_table()
            self.apply_loaded_data()
        else:
            self.fill_table()


        

    def fill_table(self):
        self.table.setRowCount(0)
        row = 0
        self.table_data = {}
        if not hasattr(self, 'network_data') or not isinstance(self.network_data, list):
            self.network_data = get_ip_info()
        def add_row(group, attr, value, editable=False, combo=False, options=None):
            nonlocal row
            self.table.insertRow(row)

            group_item = QTableWidgetItem("")
            group_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            attr_item = QTableWidgetItem(attr)
            attr_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

            self.table.setItem(row, 0, group_item)
            self.table.setItem(row, 1, attr_item)

            if editable and combo and options:
                combo_box = QComboBox()
                combo_box.addItems(options)
                combo_box.setCurrentText(value)
                self.table.setCellWidget(row, 2, combo_box)
                self.widgets[attr] = combo_box
            elif editable:
                val_item = QTableWidgetItem(value)
                self.table.setItem(row, 2, val_item)
                self.widgets[attr] = val_item
            else:
                val_item = QTableWidgetItem(value)
                val_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 2, val_item)

            row += 1

        def add_group(title):
            nonlocal row
            self.table.insertRow(row)
            item = QTableWidgetItem(title)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, item)
            self.table.setSpan(row, 0, 1, 3)
            row += 1

        name = self.system_info[0] if self.computer_id and hasattr(self, 'system_info') else platform.node()
        if self.computer_id and hasattr(self, 'system_info'):
            os_full = self.system_info[1]
        else:
            os_name, os_edition, os_arch = get_os_info()
            os_full = f"{os_name} {os_edition} ({os_arch})"

        add_group("Система")
        add_row("Система", "Имя компьютера", name)
        add_row("Система", "Операционная система", os_full, editable=False)
        add_row("Система", "Тип ARM", "", editable=True, combo=True, options=["Стационарный", "Мобильный"])
        add_row("Система", "Тип устройства", "", editable=True, combo=True, options=["Системный блок", "Ноутбук", "Моноблок", "Планшетное устройство"])

        add_group("Сеть")
        ip_data = self.network_data if hasattr(self, 'network_data') else get_ip_info()

        found_standard = False
        for iface in ip_data:
            name_iface, ip, mac, mask = iface
            if (ip.startswith("10.") or ip.startswith("192.")) and not mac.startswith("0"):
                add_row("Сеть", "IP-адрес", ip)
                add_row("Сеть", "MAC-адрес", mac)
                add_row("Сеть", "Маска", mask)
                found_standard = True

        if not found_standard:
            # если не найдено – добавить редактируемые пустые строки
            add_row("Сеть", "IP-адрес", "", editable=True)
            add_row("Сеть", "MAC-адрес", "", editable=True)
            add_row("Сеть", "Маска", "", editable=True)

       


        disks = [
            {"name": d[0], "serial": d[1], "size": d[2], "label": d[0]} 
            for d in self.disk_data
        ] if hasattr(self, 'disk_data') else get_disks()
        for i, d in enumerate(sorted(disks, key=lambda x: x['label'] or x['name'])):
            label = d["label"] or d["name"]
            add_group(f"Жесткий диск ({label})")
            add_row(f"Жесткий диск ({label})", "Имя", d["name"])
            add_row("", "Серийный номер", d["serial"])
            add_row(f"Жесткий диск ({label})", "Размер", str(d["size"]))

        add_group("Прочее")
        add_row("Прочее", "ИСОД МВД", "ИСОД МВД России")
        add_row("Прочее", "Организация", "ФКУ НПО \"СТиС\" МВД России")
        add_row("Прочее", "Город", "г. Москва")
        add_row("Прочее", "Аппарат", "Центральный аппарат МВД России")
        add_row("Прочее", "ДСТ", "", editable=True, combo=True, options=self.load_list("dst", "name"))
        add_row("Прочее", "Серийный номер", "", editable=True)
        add_row("Прочее", "Ответственное лицо", "", editable=True)
        add_row("Прочее", "Адрес", "", editable=True, combo=True, options=self.load_list("addresses", "address"))
        add_row("Прочее", "Системный администратор", "", editable=True, combo=True, options=self.load_list("admins", "name"))

    def get_cell_value(self, row, column=2):
        widget = self.table.cellWidget(row, column)
        if widget is not None:
            if isinstance(widget, QComboBox):
                return widget.currentText()
        item = self.table.item(row, column)
        if item is not None:
            return item.text()
        return ""

    def extract_table_value(self, group: str, field: str) -> str:
        current_group = None
        for row in range(self.table.rowCount()):
            group_item = self.table.item(row, 0)
            attr_item = self.table.item(row, 1)
            if group_item and group_item.text().strip():
                current_group = group_item.text()
            if attr_item and current_group == group and attr_item.text() == field:
                return self.get_cell_value(row)
        return ""

    def save_data(self):
        values = {k: (v.currentText() if isinstance(v, QComboBox) else v.text()) for k, v in self.widgets.items()}
        name = self.system_info[0] if self.computer_id and hasattr(self, 'system_info') else platform.node()

        if self.computer_id and hasattr(self, 'system_info'):
            os_full = self.system_info[1]
        else:
            os_name, os_edition, os_arch = get_os_info()
            os_full = f"{os_name} {os_edition} ({os_arch})"

        # Считывание данных из таблицы
        ip = self.extract_table_value("Сеть", "IP-адрес")
        mac = self.extract_table_value("Сеть", "MAC-адрес")
        mask = self.extract_table_value("Сеть", "Маска")

        # Подготовка дисков
        disks = [
            {"name": d[0], "serial": d[1], "size": d[2], "label": d[0]}
            for d in self.disk_data
        ] if hasattr(self, 'disk_data') else get_disks()

        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        try:
            if self.computer_id:
                cur.execute("""
                UPDATE computers SET
                    ip = ?, mac = ?, os_full = ?, user = ?, dst = ?, address = ?, admin = ?,
                    arm_type = ?, device_type = ?, serial_number = ?
                WHERE id = ?
                """, (
                    ip,
                    mac,
                    os_full,
                    values.get("Ответственное лицо", ""),
                    values.get("ДСТ", ""),
                    values.get("Адрес", ""),
                    values.get("Системный администратор", ""),
                    values.get("Тип ARM", ""),
                    values.get("Тип устройства", ""),
                    values.get("Серийный номер", ""),
                    self.computer_id
                ))
                comp_id = self.computer_id
            else:
                cur.execute("""
                INSERT INTO computers (name, ip, mac, os_full, user, dst, address, admin, arm_type, device_type, serial_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    ip,
                    mac,
                    os_full,
                    values.get("Ответственное лицо", ""),
                    values.get("ДСТ", ""),
                    values.get("Адрес", ""),
                    values.get("Системный администратор", ""),
                    values.get("Тип ARM", ""),
                    values.get("Тип устройства", ""),
                    values.get("Серийный номер", "")
                ))
                self.computer_id = cur.lastrowid
                comp_id = self.computer_id

            # Удаляем старые записи интерфейсов
            cur.execute("DELETE FROM network_interfaces WHERE computer_id = ?", (comp_id,))

            # Сохраняем основную сеть (regular)
            if ip and (ip.startswith("10.") or ip.startswith("192.")):
                cur.execute("INSERT INTO network_interfaces (computer_id, type, ip, mac, mask) VALUES (?, ?, ?, ?, ?)",
                            (comp_id, "regular", ip, mac, mask))

            # Обновляем данные по дискам
            cur.execute("DELETE FROM disks WHERE computer_id = ?", (comp_id,))
            
            for d in disks:
                cur.execute("INSERT INTO disks (computer_id, name, serial, size) VALUES (?, ?, ?, ?)",
                            (comp_id, d["name"], d["serial"], d["size"]))

            conn.commit()
            QMessageBox.information(self, "Успешно", f"Компьютер сохранён. IP: {ip}")

        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить данные: {e}")

        finally:
            conn.close()




    def prepare_data(self):
        if not self.computer_id:
            return
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
             base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")
    
        conn = sqlite3.connect(db_path)
        
        cur = conn.cursor()
        cur.execute("""
            SELECT name, os_full, user, dst, address, admin, arm_type, device_type, serial_number
            FROM computers WHERE id = ?
        """, (self.computer_id,))
        self.system_info = cur.fetchone()

        cur.execute("SELECT type, ip, mac, mask FROM network_interfaces WHERE computer_id = ?", (self.computer_id,))
        self.network_data = cur.fetchall()

        cur.execute("SELECT name, serial, size FROM disks WHERE computer_id = ?", (self.computer_id,))
        self.disk_data = cur.fetchall()

        conn.close()
    def apply_network_data(self):
        if not self.network_data:
            return

        # Сначала очистим соответствующие строки таблицы, если нужно
        # Или, если таблица полностью формируется заново, очистить полностью:
        self.table.setRowCount(0)
        row = 0

        def add_group(title):
            nonlocal row
            self.table.insertRow(row)
            item = QTableWidgetItem(title)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, item)
            self.table.setSpan(row, 0, 1, 3)
            row += 1

        def add_row(group, attr, value, editable=False, combo=False, options=None):
            nonlocal row
            self.table.insertRow(row)
            group_item = QTableWidgetItem("" if group != title else group)
            group_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            attr_item = QTableWidgetItem(attr)
            attr_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            val_item = QTableWidgetItem(value)
            if not editable:
                val_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, group_item)
            self.table.setItem(row, 1, attr_item)
            self.table.setItem(row, 2, val_item)
            row +=1

        # Разделяем интерфейсы по типу
        regular_ifaces = [iface for iface in self.network_data if iface[0] == 'regular']
    

        # Заполняем группу Сеть
        if regular_ifaces:
            add_group("Сеть")
            for _, ip, mac, mask in regular_ifaces:
                add_row("Сеть", "IP-адрес", ip, editable=True)
                add_row("Сеть", "MAC-адрес", mac, editable=True)
                add_row("Сеть", "Маска", mask, editable=True)

        # Заполняем группу Сеть client
    
    
    def apply_loaded_data(self):
            if not self.system_info:
                return

            name, os_str, user, dst, address, admin, arm_type, device_type, serial_number = self.system_info

            def set_value(field, value):
                widget = self.widgets.get(field)
                if widget:
                    if isinstance(widget, QComboBox):
                        index = widget.findText(value)
                        if index != -1:
                            widget.setCurrentIndex(index)
                    else:
                        widget.setText(value)

            set_value("Имя компьютера", name)
            set_value("Операционная система", os_str)
            set_value("Ответственное лицо", user)
            set_value("Тип ARM", arm_type)
            set_value("Тип устройства", device_type)
            set_value("ДСТ", dst)
            set_value("Адрес", address)
            set_value("Системный администратор", admin)
            set_value("Серийный номер", serial_number)
            if not self.computer_id:
                return

            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            db_path = os.path.join(base_path, "computers.db")
    
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT name, os_full, user, dst, address, admin, arm_type, device_type, serial_number
                FROM computers WHERE id = ?
            """, (self.computer_id,))
            result = cur.fetchone()

            cur.execute("SELECT type, ip, mac, mask FROM network_interfaces WHERE computer_id = ?", (self.computer_id,))
            self.network_data = cur.fetchall()

            cur.execute("SELECT name, serial, size FROM disks WHERE computer_id = ?", (self.computer_id,))
            self.disk_data = cur.fetchall()

            conn.close()
            if not result:
                return

            name, os_str, user, dst, address, admin, arm_type, device_type, serial_number = result

            def set_value(field, value):
                widget = self.widgets.get(field)
                if widget:
                    if isinstance(widget, QComboBox):
                        index = widget.findText(value)
                        if index != -1:
                            widget.setCurrentIndex(index)
                    else:
                        widget.setText(value)

            set_value("Имя компьютера", name)
            set_value("Операционная система", os_str)
            set_value("Ответственное лицо", user)
            set_value("Тип ARM", arm_type)
            set_value("Тип устройства", device_type)
            set_value("ДСТ", dst)
            set_value("Адрес", address)
            set_value("Системный администратор", admin)
            set_value("Серийный номер", serial_number)

    def load_list(self, table, column):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_path = os.path.join(base_path, "computers.db")

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT {column} FROM {table}")
        rows = [r[0] for r in cur.fetchall()]
        conn.close()
        return rows
