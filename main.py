from PyQt6.QtWidgets import QApplication, QWidget

if __name__ == "__main__":
    import sys

    app = QApplication(sys.venv)
    window = QtWidgets()
    
    window.show()

    sys.exit(app.exec())