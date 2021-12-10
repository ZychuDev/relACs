"""
    The relACs is a analysis tool for magnetic data for SMM systems using
    various models for ac magnetic characteristics and the further reliable
    determination of diverse relaxation processes.

    Copyright (C) 2021  Wiktor Zychowicz & Mikolaj Zychowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" 

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