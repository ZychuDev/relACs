from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

from view.MainPage import *

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainPage(MainWindow)

    

    MainWindow.showMaximized()

    sys.exit(app.exec_())