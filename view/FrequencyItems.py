from PyQt5 import QtWidgets
from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu

from PyQt5.QtCore import Qt

import pandas as pd
import numpy as np

import keyboard

class Relaxation():
    def __init__(self):
        self.previous = {"alpha": 0.1, "beta": 0.1, "tau" : -1.0, "chiT" : 0.0, "chiS" : 0.0}
        self.current = {"alpha": 0.1, "beta": 0.1, "tau" : -1.0, "chiT" : 0.0, "chiS" : 0.0}

        
        self.error = [0,0,0,0,0]
        self.current_error = [0,0,0,0,0]

class FitFrequencyItem(StandardItem):
    def __init__(self, mainPage, df, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.wasSaved = False
        self.relaxations = [Relaxation()]

        
        self.name = txt
        self.df = df.copy()
        try:
            self.df.drop("Show")
        except:
            pass

        self.df["Show"] = pd.Series(np.ones(len(df["Frequency"])), index=df.index)

        self.setUserTristate(True)
        self.setCheckState(Qt.Unchecked)

    def add_relaxation(self):
        self.relaxations.append(Relaxation())

    def showMenu(self, position):
        menu = QMenu()
        
        menu.addAction("Inspect fit", self.changePage)
        menu.addAction("Save to file", self.save_to_file)
        menu.addAction("Rename", self.rename)
        menu.addAction("Remove", self.remove)

        
        menu.exec_(self.ui.window.mapToGlobal(position))

    def show(self):
        i = 0
        for r in self.relaxations:
            self.ui.spinBoxRelaxation.setValue(i + 1)
            for key in self.ui.editFit2D:
                r.current[key] = float(self.ui.editFit2D[key].text())
            i += 1

        
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)
        self.ui.actualFitLabel.setText(self.name)

        self.ui.plotFr.change(self)
        self.ui.plotChi.change(self)
        self.ui.plotMain.change(self)

    # def refresh(self):
    #     for r in self.relaxations:
    #         for key in self.ui.editFit2D:
    #             r.current[key] = float(self.ui.editFit2D[key].text())

    #     self.ui.plotFr.refresh()
    #     self.ui.plotChi.refresh()
    #     self.ui.plotMain.refresh()

        
    def changePage(self, old = None):
        editFit2D = self.ui.editFit2D
        i = 0
        for r in self.relaxations:
            self.ui.spinBoxRelaxation.setValue(i + 1)
            if self.ui.checkBoxRemember.checkState() and old is not None:
                
                for key in editFit2D:
                    editFit2D[key].setText(str(old.relaxations[i].current[key]))
                    self.relaxations[i].current[key] = old.relaxations[i].current[key]

            if not self.ui.checkBoxRemember.checkState():
                for key in editFit2D:
                    editFit2D[key].setText(str(r.previous[key]))

            for param in list(self.ui.editFit2D.keys()):
                self.ui.plotFr.value_edited(param)

            i += 1

        self.show()
         
        
    def double_click(self):
        self.changePage()
        
    def click(self):   
        if keyboard.is_pressed('ctrl'):
            if self.checkState() == Qt.Unchecked:
                self.setCheckState(Qt.Checked)
            else:
                self.setCheckState(Qt.Unchecked)
            return

        self.show()


    def remove(self):
        self.parent().names.remove(self.name)
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
        nr_of_relax = 0
        while nr_of_relax < len(self.relaxations):
            r = self.relaxations[nr_of_relax]
            i = 0
            for name in r.previous:
                row = {'Name': name + str(nr_of_relax + 1), 'Value': r.previous[name], 'Error': r.error[i]}
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
                yy.append(self.ui.plotFr.model(np.log10(x), r.previous['alpha'], r.previous['beta'], r.previous['tau'], r.previous['chiT'], r.previous['chiS']))
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

            nr_of_relax += 1

        return df

    def rename(self):
        return


class FitFrequencyCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

        self.ui = mainPage
        self.names = set()


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Make fit", self.make_fit)
        menu.addAction("Save all to file", self.save_to_file)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def make_fit(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    def append(self, item):
        if item.name in self.names:
            print("FitItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.names.add(item.name)
        
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