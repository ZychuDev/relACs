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

from PyQt5.QtGui import QDoubleValidator

from PyQt5.QtCore import QLocale
from matplotlib.pyplot import plot


class Validator(QDoubleValidator):
    def __init__(self, fitItem, param, lineEdit):
        compound = fitItem.parent().parent()
        bottom = compound.ranges[param][0]
        top = compound.ranges[param][1]
        super().__init__(bottom, top, 9)
        self.fitItem = fitItem
        self.param = param
        self.lineEdit = lineEdit

        #excluding comma form valid input
        l = QLocale(QLocale.c())
        l.setNumberOptions(QLocale.RejectGroupSeparator)
        self.setLocale(l)

    def fixup(self, a0: str) -> str:
        try:
            a0 = self.lineEdit.setText(str(self.fitItem.relaxations[0].current[self.param]))
        except Exception:
            a0 = self.lineEdit.setText(str(self.fitItem.current[self.param]))

        return a0