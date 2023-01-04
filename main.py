"""
    The relACs is a analysis tool for magnetic data for SMM systems using
    various models for ac magnetic characteristics and the further reliable
    determination of diverse relaxation processes.

    Copyright (C) 2023  Wiktor Zychowicz & Mikolaj Zychowicz

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

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from views import MainView

class RelACs(QApplication):
    def __init__(self, sys_argv:list[str]):
        super(RelACs, self).__init__(sys_argv)
        self.main_view: MainView = MainView()
        app_icon: QIcon = QIcon("./assets/img/relACs.ico")
        RelACs.setWindowIcon(app_icon) 
        self.main_view.showMaximized()

if __name__ == "__main__":
    app:QApplication = RelACs(sys.argv)
    # app.setStyle("Fusion")
    sys.exit(app.exec())