from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QInputDialog
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

        self.current = {'Adir': 1,
        'Ndir': 0,
        'B1': 1,
        'B2': 1,
        'B3': 1,
        'CRaman': 0,
        'NRaman': 0,
        'NHRaman': 0,
        'Tau0': 0.1,
        'DeltaE': 0
        }


    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

        self.ui.plot3d.refresh()
        self.ui.slice.refresh()

    def change(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

        self.ui.plot3d.change(self)
        self.ui.slice.change(self)
        # self.ui.plotMain.change()
    
    def rename(self):
        text, ok = QInputDialog.getText(self.ui.window, 'Renaming dataPoint', 'Enter new dataPoint name:')
        names = self.parent().container
        if ok:
            if text in names:
                print("Name already taken")
                return

            names.pop(self.name, None)

            self.name = str(text)
            names[self.name] = self
            self.setText(self.name)

    def remove(self):
        self.parent().removeRow(self.index().row()) 


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Inspect", self.show)
        menu.addAction("Rename", self.rename)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def double_click(self):
        self.show()

    def click(self):
        self.show()


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

        if i == 0:
            return
            
        tau_item = FitTauItem(self.ui, txt='First')
        tau_item.points = points
        unzipped = pd.Series(list(zip(*points)))
        tau_item.tau = pd.Series(list(unzipped[0]))
        tau_item.temp = pd.Series(list(unzipped[1]))
        tau_item.field = pd.Series(list(unzipped[2]))

        print('#########')
        print(points)
        print(tau_item.tau)
        print(tau_item.tau.tolist() )
        print('#########')

        if self.append(tau_item) == True:
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
    



