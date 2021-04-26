from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu

import pandas as pd
import numpy as np

class FitFrequencyItem(StandardItem):
    def __init__(self, mainPage, df, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.previous = {"alpha": 1.0, "beta": 1.0, "tau" : 1.0, "chiT" : 1.0, "chiS" : 1.0}
        self.current = {"alpha": 1.0, "beta": 1.0, "tau" : -1.0, "chiT" : 1.0, "chiS" : 1.0}

        self.name = txt
        self.df = df.copy()
        try:
            self.df.drop("Show")
        except:
            pass

        self.df["Show"] = pd.Series(np.ones(len(df["Frequency"])), index=df.index)

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Inspect fit", self.show)
        menu.addAction("Rename", self.rename)
        
        menu.exec_(self.ui.window.mapToGlobal(position))

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

        self.ui.plotFr.change(self)
        self.ui.plotChi.change(self)
        self.ui.plotMain.change(self)

    def rename(self):
        return


class FitFrequencyCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

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