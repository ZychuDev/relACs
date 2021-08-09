from PyQt5.QtGui import QDoubleValidator

from PyQt5.QtCore import QLocale
from matplotlib.pyplot import plot


class Validator(QDoubleValidator):
    def __init__(self, fitItem, param, lineEdit):
        bottom = AppState.ranges[param][0]
        top = AppState.ranges[param][1]
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