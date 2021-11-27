from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

import src.AppStateBase
from src.MainPage import *

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app_icon = QIcon('./assets/img/relac-fin.ico')
    app.setWindowIcon(app_icon)
    
    screen = app.primaryScreen()
    size = screen.size()
    AppState.screen_size = (size.width(), size.height())
    rect = screen.availableGeometry()
    MainWindow = QMainWindow()
    ui = MainPage(MainWindow)

    MainWindow.showMaximized()

    sys.exit(app.exec_())