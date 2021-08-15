from .StandardItem import StandardItem
from PyQt5.QtCore import  Qt

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QInputDialog
from PyQt5 import QtWidgets
from .Plot3D import *

import pandas as pd
import numpy as np

import functools

class FitTauItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.name = txt

        self.error = [0,0,0,0,0,0,0,0,0,0]
        self.current_error = [0,0,0,0,0,0,0,0,0,0]

        self.previous = {'Adir': 1,
        'Ndir': 0,
        'B1': 1,
        'B2': 1,
        'B3': 1,
        'CRaman': 0,
        'NRaman': 0,
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
        'Tau0': 0.1,
        'DeltaE': 0
        }


    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

        self.ui.plot3d.refresh()
        self.ui.slice.refresh()

    def change(self):
        self.ui.plot3d.change(self)
        self.ui.slice.change(self)
        self.ui.slice_change_const()

        self.ui.comboBox_slice.setCurrentIndex(0)
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    def set_current_as_saved(self):
        for param in self.current:
            self.current[param] = self.previous[param]

        for i in range(len(self.error)):
            self.current_error[i] = self.error[i]


        
        for key in self.ui.edit3D:
            if key in AppState.log_params:
                self.ui.edit3D[key].setText(str(round(np.log10(self.current[key]), 9)))

            else:
                self.ui.edit3D[key].setText(str(round(self.current[key], 9)))

            self.ui.plot3d.value_edited(key, True)
        self.show()



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
        menu.addAction("Inspect", self.change)
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
        self.change()

    def click(self):
        self.change()


class FitTauCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.markColor = QColor(46,184,199)
        #self.setBackground(markColor)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Save all to file", self.save_to_file)
        menu.exec_(self.ui.window.mapToGlobal(position))

    def save_to_file(self):
        df = pd.DataFrame()
        i = 0
        while(self.child(i) != None):
            df = pd.concat([df, self.child(i).result()], axis=1)
            i += 1
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')
        try:
            with  open(name[0] + '.csv', 'w') as f:
                df.to_csv(f.name, index=False, sep= AppState.separator)
        except Exception as e:
            print(e)
            return

    def make_new_fit(self, nr_of_relax=1):
        
        f_items = self.parent().child(nr_of_relax)
        
       
        for r in range(nr_of_relax):
            i = 0
            points = []
            while(f_items.child(i) != None):
                f_item = f_items.child(i) #frequency_item
                if f_item.checkState() == Qt.Checked:
                    params = f_item.relaxations[r].previous
                    tau = np.power(10, params['tau'])
                    temp = round((f_item.df["Temperature"].max() + f_item.df["Temperature"].min())/2, 1)
                    field = round((f_item.df["MagneticField"].max() + f_item.df["MagneticField"].min())/2, 0)
                    point = (tau,temp,field)
                    points.append(point)

                i += 1

            if len(points) == 0:
                return
            name, ok = QInputDialog.getText(self.ui.window, 'Creating tau fit', 'Enter name of fit:')
            if ok:
                if r == 0:
                    tau_item = FitTauItem(self.ui, txt= name +'_relax_1')
                else:
                    tau_item = FitTauItem(self.ui, txt= name+ '_relax_2')

                tau_item.points = points
                unzipped = pd.Series(list(zip(*points)))
                tau_item.tau = pd.Series(list(unzipped[0]))
                tau_item.temp = pd.Series(list(unzipped[1]))
                tau_item.field = pd.Series(list(unzipped[2]))

                if self.append(tau_item) == True:
                    self.append(tau_item)
                tau_item.change()

            self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    # def show(self):
    #     self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    #     self.ui.plot3d.change(self)


    def append(self, item):
        if item.name in self.container:
            print("TauFiTItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
    



