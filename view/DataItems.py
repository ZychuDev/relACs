from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import  QFileDialog, QMenu, QInputDialog
from PyQt5.QtCore import  Qt, QLocale


import keyboard

from PyQt5 import QtWidgets

import os

import pandas as pd
import numpy as np


from .Plots import *
from .StandardItem import StandardItem

from model.dataFrameModel import pandasModel

from PyQt5.QtCore import Qt
from .FrequencyItems import *

from functools import partial
from .SortModes import SortModes

import configparser
import json 

class DataItem(StandardItem):
    columnsHeadersInternal = ["Temperature","MagneticField","ChiPrime","ChiBis","Frequency"]
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False,
      color=QColor(0,0,0), sort_mode=SortModes.TEMP):

        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.name = txt
        self.df = pd.DataFrame(columns=self.columnsHeadersInternal)
        self.setToolTip(txt)

        self.setUserTristate(True)
        self.setCheckState(Qt.Unchecked)
        self.sort_mode = sort_mode

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
        jsonable = {"name": self.name, "df":self.df.to_json(), "state":self.checkState(), "sort_mode":int(self.sort_mode)}
        return jsonable

    def save_to_json(self):
        jsonable = self.get_jsonable()
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')

        if name == "":
            return

        with  open(name[0] + '.json' if len(name[0].split('.')) == 1 else name[0][:-5] + '.json', 'w') as f:
            json.dump(jsonable, f)

    def from_json(self, json):
        self.name = json["name"]
        self.df = pd.read_json(json['df'])
        self.state = json['state']
        self.sort_mode = SortModes(json['sort_mode'])

    def dfToDataItem(ui, df, sufix=''):
        temp = round((df["Temperature"].max() + df["Temperature"].min())/2, 1)
        field = round((df["MagneticField"].max() + df["MagneticField"].min())/2, 0)

        name = f"T: {temp}K H: {field}Oe {sufix}"

        result = DataItem(ui, name)
        length = len(df["Frequency"])
        df["Selected"] = pd.Series(np.zeros(length), index=df.index)
        result.df =df
        result.temp = temp
        result.field = field
        return result

    def action(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.dataInspect)

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Inspect data", self.show)
        menu.addAction("Rename", self.rename)
        menu.addAction("Remove", self.remove)
        menu.addSeparator()
        menu.addAction("Save", self.save_to_json)
        menu.addSeparator()
        menu.addAction("Make fit with 1 relaxation process", self.make_fit)
        menu.addAction("Make fit with 2 relaxation process", self.make_fit_2)
        menu.exec_(self.ui.window.mapToGlobal(position))
        
        return

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.dataInspect)
        self.ui.pointPlotChi1.change(self)
        self.ui.pointPlotChi2.change(self)
        self.ui.pointPlotChi.change(self)
        self.ui.table.setModel(pandasModel(self.df))


        header = self.ui.table.horizontalHeader() 
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        for i in range(1, self.ui.table.model().columnCount()):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

        for i in range(0,self.ui.table.model().rowCount()):
            self.ui.table.selectRow(i)
        
    def double_click(self):
        self.show()

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
        

    def rename(self):
        text, ok = QInputDialog.getText(self.ui.window, 'Renaming dataPoint', 'Enter new dataPoint name:')
        names = self.parent().names
        if ok:
            if text in names:
                print("Name already taken")
                return

            names.remove(self.name)

            self.name = str(text)
            names.add(self.name)
            self.setText(self.name)

    def make_fit(self, show=True):
        fit = FitFrequencyItem(self.ui, self.df, self.parent().parent(), self.name + "FitFrequency")
        fit.temp = self.temp
        fit.field = self.field
        fit.sort_mode = self.parent().parent().child(1).sort_mode
        self.parent().parent().child(1).append(fit)
        if show:
            fit.changePage()

    def make_fit_2(self, show=True):
        fit = FitFrequencyItem(self.ui, self.df,self.parent().parent(), self.name + "FitFrequency2Relaxations")
        fit.add_relaxation()

        fit.temp = self.temp
        fit.field = self.field
        fit.sort_mode = self.parent().parent().child(2).sort_mode
        self.parent().parent().child(2).append(fit)
        if show:
            fit.changePage()

    
    


class DataCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.names = set()
        self.sort_mode = SortModes.TEMP


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Load from file", self.loadFromFile)
        menu.addAction("Make fits from all loaded data", self.make_all_fits)
        menu.addAction("Make fits from checked data", self.make_fits_checked)
        menu.addAction("Make 2-relaxations fits from checked data", self.make_fits_checked_2)
        menu.addSeparator()
        menu.addAction("Check all", self.check_all)
        menu.addAction("Uncheck all", self.uncheck_all)
        menu.addSeparator()
        menu.addAction("Load from save", self.load_from_json)
        menu.addSeparator()
        submenu = menu.addMenu("Sort")
        submenu.addAction("Sort by temperature", partial(self.sort, SortModes.TEMP))
        submenu.addAction("Sort by field", partial(self.sort, SortModes.FIELD))
        menu.addSeparator()
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
        

    def load_from_json(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile) #TMP

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

        data_item = DataItem(self.ui)
        data_item.from_json(jsonable)
        i = 2
        if data_item.name in self.names:
            saved_name = data_item.name
            data_item.name = saved_name + f"_{i}"
        while(data_item.name in self.names):
            i += 1
            data_item.name = saved_name + f"_{i}"

        data_item.setText(data_item.name)
        data_item.setCheckState(data_item.state)

        data_item.sort_mode = self.sort_mode

        self.append(data_item)
        data_item.show()

    def loadFromFile(self):
        # TO DO: implement more complex custom dialog file
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile) #TMP

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

        #.dat -> .csv nocverter, streaping unusefull header info
        with open(filepath,"r") as f:
            lines = f.readlines()
            if filepath.find('.'):
                filepath = filepath[:filepath.rfind('.')]

            filepath = filepath + ".csv"

            with open(filepath, "w+") as f:
                header = True
                for line in lines:
                    if line.strip("\n") == "[Data]":
                        header = False
                    if not header:
                        f.write(line + "\n")
        
        data = pd.read_csv(filepath, header=1)
        data = data.sort_values("Temperature (K)")

        config = configparser.RawConfigParser()
        config.optionxform = str

        config.read('view/default_settings.ini')

        translateExternalToInternal = {value:key for key, value in dict(config['Headers']).items()}
        print(f"Nowy słownik{translateExternalToInternal}")
        

        # for i in range(len(DataItem.columnsHeadersInternal)):
        #     translateExternalToInternal[AppState.columnsHeadersExternal[i]] = DataItem.columnsHeadersInternal[i]

        data = data.rename(columns=translateExternalToInternal)
        data = data[DataItem.columnsHeadersInternal]

        molar_mass = self.parent().molar_mass
        #probe_mass, status = QtWidgets.QInputDialog.getDouble(self.ui.window, 'Loading data', 'Enter sample mass:', decimals=8, min=0.0)
        dialog = QInputDialog()
        dialog.setInputMode(QInputDialog.DoubleInput)
        dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        dialog.setLabelText('Enter sample mass in grams:')
        dialog.setDoubleMinimum(0.0)
        dialog.setDoubleMaximum(1000000.0)
        dialog.setDoubleDecimals(8)
        dialog.setWindowTitle('Loading data')
        status = dialog.exec_()
    
        if status != True:
           return
        #probe_mass = 0.01 # TO DO:: value form dialog window
        probe_mass = dialog.doubleValue()
        data["ChiPrimeMol"] = data["ChiPrime"] * molar_mass/probe_mass
        data["ChiBisMol"] = data["ChiBis"] * molar_mass/probe_mass
        data["Omega"] = 2 * data["Frequency"] * np.pi
        data["OmegaLog"] = np.log10(data["Omega"])
        data["FrequencyLog"] = np.log10(data["Frequency"])
        sLength = len(data["Frequency"])

        data = data.sort_values("Temperature")
        fields = self.cluster(data, "MagneticField", float(config['Epsilons']['Field']))
        for i in list(range(0, len(fields))):
            fields[i] = self.cluster( fields[i], "Temperature", float(config['Epsilons']['Temp']))

        sufix = filepath.split('/')[-1][:-4] #extract filename from filepath
        print(sufix)
        for x in fields:
            for y in x:
                self.append(DataItem.dfToDataItem(self.ui, y, sufix))

        self.ui.TModel.resizeColumnToContents(0)
        #self.make_all_fits()# TMP

        

    def cluster(self, data, by, eps, reindex=False):
            data = data.sort_values(by=by).copy()
            minValue = data[by].min()

            results = []
            df = pd.DataFrame(columns=data.columns)
            for index, row in data.iterrows():
                if row[by] <= minValue + eps:
                    df.loc[-1] = row
                    df.index = df.index + 1
                else:
                    results.append(df)
                    df = pd.DataFrame(columns=data.columns)
                    minValue = row[by]
                    df.loc[-1] = row
                    df.index = df.index + 1

            results.append(df)

            if reindex:
                for i in range(0,len(results)):
                    results[i] = results[i].sort_values(by, ascending=False).reset_index(drop=True)
            
            for i in range(0,len(results)):
                    results[i] = results[i].sort_values("Omega")
            return results

    def append(self, item):
        if item.name in self.names:
            print("DataItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.names.add(item.name)
        #self.ui.TModel.resetHorizontalScrollMode()

    def make_all_fits(self):
        i = 0 
        while(self.child(i) != None):
            self.child(i).make_fit(False)
            i += 1
        if self.child(i-1) is not None:
            self.child(i-1).show()

        self.ui.TModel.expandAll()
    

    def remove_selected(self):
        # indexes = self.ui.TModel.selectionModel().selectedIndexes()

        # i = 0
        # nr_of_rows = self.rowCount()
        # while i < nr_of_rows:
        #     if self.child(i).index() in indexes:
        #         print(f"{i} - selected")
        #         self.removeRow(i)
        #         nr_of_rows -= 1
        #         i -= 1
        #         indexes = self.ui.TModel.selectionModel().selectedIndexes()

        #     i += 1

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

    def check_all(self):
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.Checked)

    def uncheck_all(self):
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.Unchecked)

    def make_fits_checked(self):
        for i in range(self.rowCount()):
            if self.child(i).checkState() == Qt.Checked:
                self.child(i).make_fit(False)
                if i == self.rowCount():
                    self.child(i).show()

    def make_fits_checked_2(self):
        for i in range(self.rowCount()):
            if self.child(i).checkState() == Qt.Checked:
                self.child(i).make_fit_2(False)
                if i == self.rowCount():
                    self.child(i).show()
        


        