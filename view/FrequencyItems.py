from PyQt5 import QtWidgets
from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QStyle, QMenu, QApplication, QMessageBox

from PyQt5.QtCore import Qt

import pandas as pd
import numpy as np

import keyboard

from functools import partial
from .SortModes import SortModes

class Relaxation():
    def __init__(self, compound):
        names = ["alpha", "beta", "tau", "chiT", "chiS"]
        self.previous = {}
        self.current = {}
        for p in names:
            self.current[p] = (compound.ranges[p][0] + compound.ranges[p][1])/2
            self.previous[p] = (compound.ranges[p][0] + compound.ranges[p][1])/2
        self.is_blocked = {"alpha": False, "beta": False, "tau" : False, "chiT" : False, "chiS" : False}

        
        self.error = [0.0,0.0,0.0,0.0,0.0]
        self.current_error = [0.0,0.0,0.0,0.0,0.0]
        self.residual_error = 0.0
        self.current_residual_error = 0.0


class FitFrequencyItem(StandardItem):
    def __init__(self, mainPage, df, compound, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.wasSaved = False
        self.compound = compound
        self.relaxations = [Relaxation(self.compound)]

        
        self.name = txt
        self.df = df.copy()
        try:
            self.df.drop("Show")
        except:
            pass

        self.df["Show"] = pd.Series(np.ones(len(df["Frequency"])), index=df.index)

        self.setUserTristate(True)
        self.setCheckState(Qt.Unchecked)

        def __lt__(self, other): 
            if self.sort_mode == SortModes.TEMP:
                if self.temp == other.temp:
                    return self.field < other.field
                return self.temp < other.temp

            if self.sort_mode == SortModes.FIELD:
                if self.field == other.field:
                    return self.temp < other.temp
                return self.field < other.field

    def add_relaxation(self):
        self.relaxations.append(Relaxation(self.compound))

    def showMenu(self, position):
        menu = QMenu()
        
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
                pass


            for key in self.ui.checkFit2D:
                self.ui.checkFit2D[key].blockSignals(True)
                self.ui.checkFit2D[key].setChecked( r.is_blocked[key]) 
                self.ui.checkFit2D[key].blockSignals(False)

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
        self.ui.plotFr.change(self)
        self.ui.plotChi.change(self)
        self.ui.plotMain.change(self)

        editFit2D = self.ui.editFit2D
        i = 0
        for r in self.relaxations:      
            self.ui.spinBoxRelaxation.setValue(i + 1)

            if not self.ui.checkBoxRemember.isChecked() or old is None:
                for key in self.ui.editFit2D:
                    self.ui.editFit2D[key].setText(str(r.previous[key]))
                    self.ui.plotFr.value_edited(key, True)

            if self.ui.checkBoxRemember.isChecked() and old is not None:
                
                for key in editFit2D:
                    editFit2D[key].setText(str(old.relaxations[i].current[key]))
                    r.current[key] = old.relaxations[i].current[key]
                    self.ui.checkFit2D[key].blockSignals(True)
                    r.is_blocked[key] = old.relaxations[i].is_blocked[key]
                    self.ui.checkFit2D[key].blockSignals(False)
                    self.ui.plotFr.value_edited(key, True)

                
            i += 1

            self.show()
         
        
    def double_click(self):
        self.click()
        
    def click(self):   
        if keyboard.is_pressed('ctrl'):
            if self.checkState() == Qt.Unchecked:
                self.setCheckState(Qt.Checked)
            else:
                self.setCheckState(Qt.Unchecked)
            return

        self.changePage()


    def remove(self):
        self.parent().names.remove(self.name)
        self.parent().removeRow(self.index().row())
        

    def save_to_file(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file', filter="*.csv")
        try:
            with  open(name[0], 'w') as f:
                self.result().to_csv(f.name, index=False, sep=AppState.separator)
        except OSError as e:
            message = str(e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(message)
            msg.setWindowTitle("Error when saving to file")
            msg.exec_()
            return

    def result(self):
        df_param = pd.DataFrame([['T', self.temp, 0], ['H', self.field, 0]], columns=['Name', 'Value','Error'])
        nr_of_relax = 0
        while nr_of_relax < len(self.relaxations):
            r = self.relaxations[nr_of_relax]
            i = 0
            for name in r.previous:
                row = {'Name': (name if name != "tau" else 'log10 '+ name)+ str(nr_of_relax + 1),
                 'Value': (r.previous[name] if name != 'chiT' else r.previous[name] + r.previous['chiS']),
                 'Error': r.error[i]}
                i += 1
                df_param = df_param.append(row, ignore_index=True)


            df_experimental = self.df[["Frequency", "ChiPrimeMol","ChiBisMol"]].loc[self.df["Show"]== True]
            df_experimental.columns = [f"Frequency T={self.temp} H={self.field}", f"ChiPrimeMol T={self.temp} H={self.field}",
             f"ChiBisMol T={self.temp} H={self.field}"]
            df_experimental.reset_index(drop=True, inplace=True)

            columns=[f"FrequencyModel T={self.temp} H={self.field}", f"ChiPrimeModelT={self.temp} H={self.field}",
             f"ChiBisModel T={self.temp} H={self.field}"]
            df_model = pd.DataFrame(columns=columns)

            shown = self.df.loc[self.df["Show"]== True] 
            xx = np.logspace(np.log10(shown["Frequency"].min()),np.log10(shown["Frequency"].max()), AppState.resolution)

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
        menu.addAction("Make fit from all checked", self.make_fit)
        menu.addAction("Save all to file", self.save_to_file)
        menu.addAction("Make all fits", self.make_fits_for_all)
        menu.addSeparator()
        menu.addAction("Check all", self.check_all)
        menu.addAction("Uncheck all", self.uncheck_all)
        menu.addSeparator()
        submenu = menu.addMenu("Sort")
        submenu.addAction("Sort by temperature", partial(self.sort, SortModes.TEMP))
        submenu.addAction("Sort by field", partial(self.sort, SortModes.FIELD))
        menu.addAction("Remove selected", self.remove_selected)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def sort(self, sort_mode=None):
        if sort_mode is not None:
            self.sort_mode = sort_mode
            
        i = 0
        while self.child(i) is not None:
            self.child(i).sort_mode = self.sort_mode
            i += 1

        self.sortChildren(0)

    def make_fit(self):
        if self.child(0) is not None:
            self.parent().child(3).make_new_fit(len(self.child(0).relaxations))

        

    def remove_selected(self):
        i = 0
        nr_of_rows = self.rowCount()
        while i < nr_of_rows:
            child = self.child(i)
            if child.checkState() == Qt.Checked:
                self.names.remove(child.name)
                self.removeRow(i)
                nr_of_rows -= 1
                i -= 1
            i += 1

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

    def make_fits_for_all(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        i = 0
        while(self.child(i) != None):
            child = self.child(i)
            child.show()
            child.ui.plotFr.make_auto_fit(auto=True)
            child.ui.plotFr.saveFit()
            i += 1
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()

    def check_all(self):
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.Checked)

    def uncheck_all(self):
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.Unchecked)