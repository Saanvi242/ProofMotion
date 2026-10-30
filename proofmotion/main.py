"""
main.py
-------
ProofMotion — An Interactive Mathematics, Algorithms and Computer Graphics Learning Platform.
Application entry point.

Wires together:
    MainWindow (ui.main_window)
    ApplicationController (controllers.application_controller)
    TheoremEngine (theorems.theorem_engine)
    AlgorithmEngine (algorithms.algorithm_engine)
    CGIP Labs (cgip.*)
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase

from ui.main_window import MainWindow
from controllers.application_controller import ApplicationController
from theorems.theorem_engine import TheoremEngine
from resources.theme import set_font_family


def load_custom_font():
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    if not os.path.isdir(resources_dir):
        return

    for filename in sorted(os.listdir(resources_dir)):
        lower = filename.lower()
        if not lower.endswith((".ttf", ".otf", ".woff", ".woff2")):
            continue

        font_path = os.path.join(resources_dir, filename)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                print(f"Loaded font: {families[0]} from {font_path}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ProofMotion")
    load_custom_font()

    installed_families = set(QFontDatabase().families())
    font_family = next(
        (family for family in ("Inter", "Segoe UI", "Arial") if family in installed_families),
        QFontDatabase.systemFont(QFontDatabase.GeneralFont).family(),
    )
    set_font_family(font_family)
    app_font = QFont(font_family)
    app_font.setPixelSize(14)
    app.setFont(app_font)

    engine = TheoremEngine()
    window = MainWindow(theorems=engine.get_theorems_list())

    controller = ApplicationController(window, engine=engine)
    window._controller = controller  # keep reference alive

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
