"""
    The relACs is a analysis tool for magnetic data for SMM systems using
    various models for ac magnetic characteristics and the further reliable
    determination of diverse relaxation processes.

    Copyright (C) 2021  Wiktor Zychowicz & Mikolaj Zychowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" 

from typing import Collection
from PyQt5 import QtWidgets
from .StandardItem import StandardItem

from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QStyle, QMenu, QApplication, QMessageBox, QInputDialog

from PyQt5.QtCore import Qt

import pandas as pd
import numpy as np

import keyboard
import os 
import json 

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
        self.current_error = np.array([0.0,0.0,0.0,0.0,0.0])
        self.residual_error = 0.0
        self.current_residual_error = 0.0

    def get_jsonable(self):
        jsonable ={'previous': self.previous, 'current': self.current,
         'is_blocked':self.is_blocked, 'error': self.error, 'current_error': list(self.current_error),
         'residual_error': self.residual_error, 'current_residual_error': self.current_residual_error
        }

        return jsonable

    def from_json(self, json):
        self.previous = json['previous']
        self.current = json['current']
        self.is_blocked = json['is_blocked']
        self.error = json['error']
        self.current_error = json['current_error']
        self.residual_error = json['residual_error']
        self.current_residual_error = json['current_residual_error']

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

    def get_jsonable(self):
        jsonable = {"was_saved": self.wasSaved, 'relaxations': [], 'name': self.name, 'df':self.df.to_json(), 'state': self.checkState(),
        'temp':self.temp, 'field':self.field, 'nr_of_relaxations': len(self.relaxations), 'sort_mode': self.sort_mode }
        
        for r in self.relaxations:
            jsonable['relaxations'].append(r.get_jsonable())

        return jsonable

    
    def save_to_json(self):
        jsonable = self.get_jsonable()
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')

        if name == "":
            return

        with  open(name[0] + '.json' if len(name[0].split('.')) == 1 else name[0][:-5] + '.json', 'w') as f:
            json.dump(jsonable, f, indent=4)

    def from_json(self, json):
        self.name = json['name']
        self.wasSaved = json['was_saved'],
        self.relaxations = []
        for r in json['relaxations']:
            relax = Relaxation(self.compound)
            relax.from_json(r)
            self.relaxations.append(relax)
        self.df = pd.read_json(json['df'])
        self.setCheckState(json['state'])

        self.temp = json['temp']
        self.field = json['field']

    def add_relaxation(self):
        self.relaxations.append(Relaxation(self.compound))

    def showMenu(self, position):
        menu = QMenu()
        
        menu.addAction("Save to file", self.save_to_file)
        # menu.addSeparator()
        # menu.addAction("Save", self.save_to_json)
        menu.addSeparator()
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
        text, ok = QInputDialog.getText(self.ui.window, 'Renaming Frequency Fit', 'Enter new Frequency Fit name:')
        names = self.parent().names
        if ok:
            if text in names:
                print("Name already taken")
                return

            names.remove(self.name)

            self.name = str(text)
            names.add(self.name)
            self.setText(self.name)


class FitFrequencyCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', nr_of_relaxations=1, font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

        self.setBackground(QBrush(QColor(255,201,183)))
            

        self.ui = mainPage
        self.names = set()
        self.sort_mode = SortModes.TEMP
        self.nr_of_relaxations = nr_of_relaxations

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Make fit from all checked", self.make_fit)
        menu.addAction("Save all to file", self.save_to_file)
        menu.addAction("Make all fits", self.make_fits_for_all)
        menu.addSeparator()
        menu.addAction("Check all", self.check_all)
        menu.addAction("Uncheck all", self.uncheck_all)
        # menu.addSeparator()
        # menu.addAction("Load from save", self.load_from_json)
        menu.addSeparator()
        submenu = menu.addMenu("Sort")
        submenu.addAction("Sort by temperature", partial(self.sort, SortModes.TEMP))
        submenu.addAction("Sort by field", partial(self.sort, SortModes.FIELD))
        menu.addAction("Remove selected", self.remove_selected)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def load_from_json(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile) #TMP

        if dlg.exec_():
           filenames = dlg.selectedFiles()
        else:
           return

        if len(filenames) != 1 :
            return 

        filepath = filenames[0]  #TMP "C:/Users/wikto/Desktop/ACMA/ac_0_Oe.dat"  #
        if not os.path.isfile(filepath):
            print("File path {} does not exist. Exiting...".format(filepath))
            return

        with open(filepath, "r") as f:
            jsonable = json.load(f)

        print(f"Fit loaded json: {jsonable}")

        frequency_item, collection = self.create_from_json(jsonable)
        collection.append(frequency_item)
        frequency_item.changePage()

    def create_from_json(self, jsonable):
        frequency_item = FitFrequencyItem(self.ui, pd.read_json(jsonable['df']), self.parent())
        frequency_item.from_json(jsonable)
        collection = self.parent().child(jsonable['nr_of_relaxations'])

        i = 2
        if frequency_item.name in collection.names:
            saved_name = frequency_item.name
            frequency_item.name = saved_name + f"_{i}"
        while (frequency_item.name in collection.names):
            i += 1
            frequency_item.name = saved_name + f"_{i}"

        frequency_item.setText(frequency_item.name)
        frequency_item.sort_mode = collection.sort_mode

        return frequency_item, collection

    def get_jsonable(self):
        items_list = []
        i = 0
        while(self.child(i) != None):
            items_list.append(self.child(i).get_jsonable())
            i += 1
        jsonable = {'items_list':items_list, 'sort_mode':self.sort_mode,
         'nr_of_relaxations': self.nr_of_relaxations}
        return jsonable

    def save_to_json(self):
        jsonable = self.get_jsonable()
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')

        if name == "":
            return

        with  open(name[0] + '.json' if len(name[0].split('.')) == 1 else name[0][:-5] + '.json', 'w') as f:
            json.dump(jsonable, f, indent=4)

    def from_json(self, json):
        for item in json['items_list']:
            frequency_item, collection = self.create_from_json(item)
            collection.append(frequency_item)
        self.nr_of_relaxations = json['nr_of_relaxations']
        self.sort_mode = json['sort_mode']

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