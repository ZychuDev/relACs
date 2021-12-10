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

from .StandardItem import StandardItem
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QMenu

class ModelItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

    def showMenu(self, position):
        menu = QMenu()
        menu.exec_(self.ui.window.mapToGlobal(position))
        
    def action(self):
        print("Clicked Fit Item")

class ModelCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=14, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.setBackground(QBrush(QColor(255,201,183)))
        self.ui = mainPage

    def showMenu(self, position):
        menu = QMenu()
        menu.exec_(self.ui.window.mapToGlobal(position))