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

from PyQt6.QtGui import QColor, QStandardItem, QFont
from PyQt6.QtCore import QPoint


class StandardItem(QStandardItem):
    def __init__(self, txt:str='', font_size:int=12, set_bold:bool=False, color:QColor=QColor(0,0,0)):
        super().__init__()
        fnt:QFont = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        #self.setIcon(jakasTam.png)
       
        self.setCheckable(False)
        self.setAutoTristate(False)
        self.setUserTristate(False)
        # self.setTristate(False)
        
    def on_double_click(self):
        print("No provided action for this item")

    def on_click(self):
        print("No provided action for single click")

    def show_menu(self, position: QPoint):
        print("This item does not support menus")

