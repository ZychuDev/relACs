from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFileDialog, QPushButton, QMenu, QTableView, QAbstractItemView, QInputDialog
from PyQt5.QtCore import  Qt, QSize, QRect, QFile

from PyQt5 import QtWidgets

import sys
import os

import pandas as pd
import numpy as np

from .Plots import *
from .StandardItem import StandardItem

from model.dataFrameModel import pandasModel

from .FrequencyItems import *


class DataItem(StandardItem):
    columnsHeadersInternal = ["Temperature","MagneticField","ChiPrime","ChiBis","Frequency"]
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        #self.columnsHeadersExternal = AppState.settings

        self.name = txt
        self.df = pd.DataFrame(columns=self.columnsHeadersInternal)
        self.setToolTip(txt)

    def dfToDataItem(ui, df, sufix=''):
        temp = round((df["Temperature"].max() + df["Temperature"].min())/2, 1)
        field = round((df["MagneticField"].max() + df["MagneticField"].min())/2, 0)

        name = f"T: {temp}K H: {field}Oe {sufix}"

        result = DataItem(ui, name)
        length = len(df["Frequency"])
        df["Selected"] = pd.Series(np.zeros(length), index=df.index)
        result.df =df
        return result

    def action(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.dataInspect)

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Inspect data", self.show)
        menu.addAction("Rename", self.rename)
        menu.addAction("Remove", self.remove)
        menu.addSeparator()
        menu.addAction("Make fit", self.makeFit)
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
        self.show()

    def remove(self):
        self.parent().removeRow(self.index().row()) 

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

    def makeFit(self):
        fit = FitFrequencyItem(self.ui, self.df, self.name + "FitFrequency")
        self.parent().parent().child(1).append(fit)
        fit.show()
    


class DataCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Load from file", self.loadFromFile)
        menu.addAction("Make fits from all laded data", self.make_all_fits)

        menu.exec_(self.ui.window.mapToGlobal(position))


    def loadFromFile(self):
        # TO DO: implement more complex custom dialog file
        # dlg = QtWidgets.QFileDialog()
        # dlg.setFileMode(QFileDialog.AnyFile) #TMP

        # if dlg.exec_():
        #     filenames = dlg.selectedFiles()
        # else:
        #     return

        # if len(filenames) != 1 :
        #      return 

        filepath =  "C:/Users/wikto/Desktop/ACMA/ac_0_Oe.dat" #TMP filenames[0] #
        if not os.path.isfile(filepath):
            print("File path {} does not exist. Exiting...".format(filepath))
            return

        #.dat -> .csv nocverter, streaping unusefull header info
        with open(filepath,"r") as f:
            lines = f.readlines()
            filepath = filepath[:-4] + ".csv"
            with open(filepath, "w+") as f:
                header = True
                for line in lines:
                    if line.strip("\n") == "[Data]":
                        header = False
                    if not header:
                        f.write(line + "\n")
        
        data = pd.read_csv(filepath, header=1)
        data = data.sort_values("Temperature (K)")

        translateExternalToInternal = {}
        for i in range(len(DataItem.columnsHeadersInternal)):
            translateExternalToInternal[AppState.columnsHeadersExternal[i]] = DataItem.columnsHeadersInternal[i]

        data = data.rename(columns=translateExternalToInternal)
        data = data[DataItem.columnsHeadersInternal]

        molarMass = self.parent().molarMass
        # probeMass, status = QtWidgets.QInputDialog.getDouble(self.ui.window, 'Loading data', 'Enter sample mass:')
        # if status != True:
        #     return
        probeMass = 0.01 # TO DO:: value form dialog window

        data["ChiPrimeMol"] = data["ChiPrime"] * molarMass/probeMass
        data["ChiBisMol"] = data["ChiBis"] * molarMass/probeMass
        data["Omega"] = 2 * data["Frequency"] * np.pi
        data["FrequencyLog"] = np.log10(data["Frequency"])
        sLength = len(data["Frequency"])

        data = data.sort_values("Temperature")
        fields = self.cluster(data, "MagneticField", AppState.epsField)
        for i in list(range(0, len(fields))):
            fields[i] = self.cluster( fields[i], "Temperature", AppState.epsTemp)

        sufix = filepath.split('/')[-1][:-4] #extract filename from filepath
        print(sufix)
        for x in fields:
            for y in x:
                self.append(DataItem.dfToDataItem(self.ui, y, sufix))

        

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
        if item.name in self.container:
            print("DataItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
        #self.ui.Model.resetHorizontalScrollMode()

    def make_all_fits(self):
        i = 0 
        while(self.child(i) != None):
            self.child(i).makeFit()
            i += 1