from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu
from .Plot3D import *

import pandas as pd
import numpy as np

class FitTauItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.name = txt

        self.previous = {'Adir': 1,
        'Ndir': 0,
        'B1': 1,
        'B2': 1,
        'B3': 1,
        'CRaman': 0,
        'NRaman': 0,
        'NHRaman': 0,
        'Tau0': 1,
        'DeltaE': 0
        }

        self.current = {'Adir': 0,
        'Ndir': 0,
        'B1': 0,
        'B2': 0,
        'B3': 0,
        'CRaman': 0,
        'NRaman': 0,
        'NHRaman': 0,
        'Tau0': 1,
        'DeltaE': 0
        }


    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

        self.ui.plot3d.change(self)

    def change(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

        self.ui.plot3D.change(self)
        # self.ui.plot2.change()
        # self.ui.plotMain.change()

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Inspect", self.show)

        menu.exec_(self.ui.window.mapToGlobal(position))


class FitTauCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.markColor = QColor(46,184,199)
        #self.setBackground(markColor)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Make new fit", self.makeNewFit)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def makeNewFit(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)
        f_items = self.parent().child(1)
        points = []
        i = 0
        while(f_items.child(i) != None):
            f_item = f_items.child(i) #frequency_item
            params = f_item.current
            tau = np.power(10, params['tau'])
            temp = round((f_item.df["Temperature"].max() + f_item.df["Temperature"].min())/2, 1)
            field = round((f_item.df["MagneticField"].max() + f_item.df["MagneticField"].min())/2, 0)
            point = (tau,temp,field)
            points.append(point)

            i += 1

        tau_item = FitTauItem(self.ui, txt='First')
        tau_item.points = points
        unzipped = list(zip(*points))
        tau_item.tau = unzipped[0]
        tau_item.temp = unzipped[1]
        tau_item.field = unzipped[2]

        #if self.append(tau_item) == True:
        self.append(tau_item)
        tau_item.change()

    # def show(self):
    #     self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    #     self.ui.plot3d.change(self)



    def append(self, item):
        if item.name in self.container:
            print("TauFiTItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
    



