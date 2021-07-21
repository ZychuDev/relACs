from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QInputDialog
from PyQt5 import QtWidgets
from .Plot3D import *

import pandas as pd
import numpy as np

class FitTauItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.name = txt

        self.error = [0,0,0,0,0]

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
        menu.addAction("Save to file", self.save_to_file)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def save_to_file(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')
        try:
            with  open(name[0] + '.csv', 'w') as f:
                self.result().to_csv(f.name, index=False, sep=AppState.separator)
        except Exception as e:
            print(e)
            return

    def result(self):
        df_param = pd.DataFrame(columns=['Name', 'Value','Error'])
        i = 0
        for p in self.current:
            row = {'Name': p, 'Value':self.current[p], 'Error':self.error[i]}
            i += 1
            df_param = df_param.append(row, ignore_index=True)

        a = pd.DataFrame(self.temp).rename(columns={0:'T'})
        b = pd.DataFrame(self.field).rename(columns={0:'H'})
        c = pd.DataFrame(self.tau).rename(columns={0:'Tau'})
        df_experimental = pd.concat([a,b,c], axis=1)

        x = np.linspace(self.temp.min(),self.temp.max(),50)
        y = np.linspace(self.field.min(),self.field.max(), 50)
        X, Y = np.meshgrid(x,y)

        a = list(self.current.values())
        Z = 1/self.ui.plot3d.model(X,Y,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9])

        temp = []
        for x in X:
            for t in x:
                temp.append(t)

        field = []
        for y in Y:
            for h in y:
                field.append(h)

        tau = []
        for z in Z:
            for v in z:
                tau.append(v)

        a=pd.DataFrame(pd.Series(temp)).rename(columns={0:'TempModel'})
        b=pd.DataFrame(pd.Series(field)).rename(columns={0:'FieldModel'})
        c=pd.DataFrame(pd.Series(tau)).rename(columns={0:'TauModel'})
        df_model = pd.concat([a,b,c], axis=1)

        return pd.concat([df_param, df_experimental, df_model], axis=1)







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
        
            for r in f_item.relaxations:
                params = r.previous
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
    



