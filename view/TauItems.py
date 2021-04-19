from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu

import pandas as pd
import numpy as np

class FitTauItem(StandardItem):
    def __init__(self, mainPage, df, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

        self.ui = mainPage

        self.name = txt
        self.df = df.copy()
        try:
            self.df.drop("Selected")
        except:
            pass

        self.df = df["Show"] = pd.Series(np.ones(len(df["Frequency"])), index=df.index)
        print(df)

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

    def change(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

        self.ui.plot1.change()
        self.ui.plot2.change()
        self.ui.plotMain.change()


class FitTauCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.markColor = QColor(46,184,199)
        #self.setBackground(markColor)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Make fit", self.makeFit)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def makeFit(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    def append(self, item):
        if item.name in self.container:
            print("DataItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
    
    def showMenu(self, position):
        menu = QMenu()
        inspect = menu.addAction("Make new fit", self.makeFit)
        action = menu.exec_(self.ui.window.mapToGlobal(position))
        return


