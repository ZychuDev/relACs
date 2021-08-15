from PyQt5 import QtWidgets

import view.AppStateBase
from view.MainPage import *

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    AppState.screen_size = (size.width(), size.height())
    rect = screen.availableGeometry()
    MainWindow = QtWidgets.QMainWindow()
    ui = MainPage(MainWindow)

    MainWindow.showMaximized()

    sys.exit(app.exec_())