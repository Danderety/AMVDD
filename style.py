from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QStyleFactory, QPushButton
from PyQt6.QtCore import Qt

def apply_light_theme(app):
    app.setStyle(QStyleFactory.create("Fusion"))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(76, 163, 224))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)

    app.setStyleSheet("""
        QComboBox {
            background-color: #e0e0e0;
            color: black;
            border: 1px solid gray;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: black;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #666;
            background-color: #f0f0f0;
        }
        QCheckBox::indicator:checked {
            background-color: #2a82da;
            image: url(:/qt-project.org/styles/commonstyle/images/checkbox_checked.png);
        }
    """)

def apply_dark_theme(app):
    app.setStyle(QStyleFactory.create("Fusion"))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)

    app.setStyleSheet("""
        QComboBox {
            background-color: #444444;
            color: white;
            border: 1px solid #888;
            border-radius: 4px;
            padding: 4px;
        }
        QComboBox QAbstractItemView {
            background-color: #222222;
            color: white;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid #aaa;
            background-color: #444444;
        }
        QCheckBox::indicator:checked {
            background-color: #00aaff;
            image: url(:/qt-project.org/styles/commonstyle/images/checkbox_checked.png);
        }
    """)

def apply_button_style(*buttons: QPushButton):
    for button in buttons:
        button.setMinimumHeight(36)
        button.setStyleSheet("""
            QPushButton {
                border: 1px solid #888;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
