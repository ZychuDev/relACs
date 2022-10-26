import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QIcon
from pandas import DataFrame # type: ignore

if __name__ == "__main__":
    app:QApplication = QApplication(sys.argv)
    app_icon: QIcon = QIcon("./assets/img/relACs.ico")
    app.setWindowIcon(app_icon)    
    window:QWidget = QWidget()
    
    window.show()

    sys.exit(app.exec())