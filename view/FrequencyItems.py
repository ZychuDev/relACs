from PyQt5 import QtWidgets
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

        self.error = [0,0,0,0,0]
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
        menu.addAction("Save to file", self.save_to_file)
        menu.addAction("Rename", self.rename)
        menu.addAction("Remove", self.remove)

        
        menu.exec_(self.ui.window.mapToGlobal(position))

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

        self.ui.plotFr.change(self)
        self.ui.plotChi.change(self)
        self.ui.plotMain.change(self)

    def double_click(self):
        self.show()
        
    def click(self):
        self.show()

    def remove(self):
        self.parent().removeRow(self.index().row())

    def save_to_file(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')
        try:
            with  open(name[0] + '.csv', 'w') as f:
                self.result().to_csv(f.name, index=False, sep=AppState.separator)
        except Exception as e:
            print(e)
            return

    def result(self):
        df_param = pd.DataFrame([['T', self.temp, 0], ['H', self.field, 0]], columns=['Name', 'Value','Error'])
        i = 0
        for name in self.current:
            row = {'Name': name, 'Value': self.current[name], 'Error': self.error[i]}
            i += 1
            df_param = df_param.append(row, ignore_index=True)


        df_experimental = self.df[["Frequency", "ChiPrimeMol", "ChiBisMol"]]
        df_experimental.reset_index(drop=True, inplace=True)

        columns=["FrequencyModel", "ChiPrimeModel", "ChiBisModel"]
        df_model = pd.DataFrame(columns=columns)
        xx = np.logspace(np.log10(self.df["Frequency"].min()),np.log10(self.df["Frequency"].max()), AppState.resolution)

        df_model[columns[0]] = pd.Series(xx)
        yy = []
        for x in xx:
            yy.append(self.ui.plotFr.model(np.log10(x), self.current['alpha'], self.current['beta'], self.current['tau'], self.current['chiT'], self.current['chiS']))
        print('yy len:', len(yy), 'yy:', yy)
        real = []
        img = []
        for c in yy:
            real.append(c.real)
            img.append(-c.imag)
        print('real: ', real)
        print('img:', img)
        df_model[columns[1]] = pd.Series(real)
        df_model[columns[2]] = pd.Series(img)

        tmp = pd.concat([df_param, df_experimental], axis=1)
        df = pd.concat([tmp, df_model], axis=1)
        return df







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
        menu.addAction("Save all to file", self.save_to_file)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def makeFit(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    def append(self, item):
        if item.name in self.container:
            print("DataItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
        
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