from .StandardItem import StandardItem
from PyQt5.QtGui import QColor
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
        self.ui = mainPage

    def showMenu(self, position):
        menu = QMenu()
        menu.exec_(self.ui.window.mapToGlobal(position))