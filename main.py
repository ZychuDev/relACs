from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import view.AppStateBase
from view.MainPage import *

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    screen = app.primaryScreen()
    print('Screen: %s' % screen.name())
    size = screen.size()
    AppState.screen_size = (size.width(), size.height())
    print('Size: %d x %d' % (size.width(), size.height()))
    rect = screen.availableGeometry()
    print('Available: %d x %d' % (rect.width(), rect.height()))
    MainWindow = QtWidgets.QMainWindow()
    ui = MainPage(MainWindow)

    MainWindow.showMaximized()

    sys.exit(app.exec_())