import sys
import json
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from style import apply_light_theme, apply_dark_theme
from database.setup import initialize_database


CONFIG_PATH = "theme_config.json"

def load_theme():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("theme", "light")
    except:
        return "light"

def save_theme(theme):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"theme": theme}, f)

def apply_theme(app, theme):
    if theme == "dark":
        apply_dark_theme(app)
    else:
        apply_light_theme(app)

def main():
    initialize_database()
    app = QApplication(sys.argv)
    theme = load_theme()
    apply_theme(app, theme)
    
    window = MainWindow(
        theme=theme,
        save_theme=save_theme,
        apply_theme=lambda t: apply_theme(app, t)
    )
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
