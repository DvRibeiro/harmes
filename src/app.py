"""Inicialização da aplicação Hermes."""

import sys
from PyQt6.QtWidgets import QApplication
from .ui.companion import CreatureCompanion


def main():
    """Ponto de entrada principal da aplicação Hermes."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    companion = CreatureCompanion()
    companion.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
