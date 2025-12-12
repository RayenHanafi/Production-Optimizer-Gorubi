import sys
from PyQt5.QtWidgets import QApplication
from ui import ProductionApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductionApp()
    window.show()
    sys.exit(app.exec_())