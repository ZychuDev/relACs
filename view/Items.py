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
        load = menu.addAction("Load from file", self.loadFromFile)

        action = menu.exec_(self.ui.window.mapToGlobal(position))


    def loadFromFile(self):
        # TO DO: implement more complex custom dialog file
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile) #TMP

        if dlg.exec_():
            filenames = dlg.selectedFiles()
        else:
            return

        if len(filenames) != 1 :
             return 

        filepath = filenames[0] # "C:/Users/wikto/Desktop/ACMA/ac_0_Oe.dat" #TMP
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

        










class FitTauItem(StandardItem):
    def __init__(self, mainPage, df, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

        self.ui = mainPage

        self.name = txt
        self.df = df.copy()
        try:
            self.df.drop("Selected")
        except:
            pass

        self.df = df["Show"] = pd.Series(np.ones(len(df["Frequency"])), index=df.index)
        print(df)

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

    def change(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

        self.ui.plot1.change()
        self.ui.plot2.change()
        self.ui.plotMain.change()


class FitTauCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.markColor = QColor(46,184,199)
        #self.setBackground(markColor)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Make fit", self.makeFit)

        menu.exec_(self.ui.window.mapToGlobal(position))

    def makeFit(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    def append(self, item):
        if item.name in self.container:
            print("DataItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
    
    def showMenu(self, position):
        menu = QMenu()
        inspect = menu.addAction("Make new fit", self.makeFit)
        action = menu.exec_(self.ui.window.mapToGlobal(position))
        return





class FitFrequencyItem(StandardItem):
    def __init__(self, mainPage, df, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.previous = {"alpha": 0, "beta": 0, "tau" : 0, "chiT" : 0, "chiS" : 0}
        self.current = {"alpha": 1, "beta": 1, "tau" : 1, "chiT" : 1, "chiS" : 1}

        self.name = txt
        self.df = df.copy()
        try:
            self.df.drop("Show")
        except:
            pass

        self.df["Show"] = pd.Series(np.ones(len(df["Frequency"])), index=df.index)
        print(self.df)

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Inspect fit", self.show)
        menu.addAction("Rename", self.rename)
        
        menu.exec_(self.ui.window.mapToGlobal(position))

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)


    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit2Dpage)

        self.ui.plotFr.change(self)
        self.ui.plotChi.change(self)
        self.ui.plotMain.change(self)

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

        menu.exec_(self.ui.window.mapToGlobal(position))

    def makeFit(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    def append(self, item):
        if item.name in self.container:
            print("DataItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item


class ModelItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

    def action(self):
        print("Clicked Fit Item")

class ModelCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=14, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

class CompoundCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=14, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.container = {}
    
    def showMenu(self, position):
        menu = QMenu()
        new = menu.addAction("New", self.action)
        action = menu.exec_(self.ui.window.mapToGlobal(position))
        if action == new:
            self.add()

    def add(self):
        name, status = QtWidgets.QInputDialog.getText(self.ui.window, "Compund Creation",
        "Enter name for new compound:")
        if status == True:
            if name in self.container:
                #TO DO: Ui information
                print("Compound already exists choose other name or delete old one!")
                return False #To DO throw exception
            new = CompoundItem(self.ui, name)
            self.appendRow(new)
            self.container[name] = new

    def append(self, compound):
        if compound.name in self.container:
            #TO DO: Ui information
            print("Compound already exists choose other name or delete old one!")
            return False #To DO throw exception
        self.appendRow(compound)
        self.container[compound.name] = compound

                

class CompoundItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0),
    molarMass = 2000):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.name = txt
        self.molarMass = molarMass #TO DO: implement dialog box option for it

        self.data = DataCollectionItem(self.ui, 'Data')
        self.FrequencyFits = FitFrequencyCollectionItem(self.ui, 'FrequencyFits(2D)')
        self.TauFits = FitTauCollectionItem(self.ui, 'TauFits(3D)')

        self.appendRow(self.data)
        self.appendRow(self.FrequencyFits)
        self.appendRow(self.TauFits)

    def addTo(self, collection):
        collection.appendRow(self)

    def showMenu(self, position):
        pass




class RootItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=16, set_bold=True, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.compounds = CompoundCollectionItem(self.ui, "Compounds")
        self.models = ModelCollectionItem(self.ui, "Models")

        self.appendRow(self.compounds)
        self.appendRow(self.models)

    def showMenu(self, position):
        return
        # menu = QMenu()
        # new = menu.addAction("New", self.action)
        # action = menu.exec_(self.ui.window.mapToGlobal(point))
        # if action == new:
        #     self.add()

    # def add(self):
    #     name, status = QtWidgets.QInputDialog.getText(self.ui.window, "Compund Creation",
    #     "Enter name for new compound:")
    #     if status == True:
    #         new = self.ui.appState.addCompound(name)
    #         if new != False:
    #             self.ui.whole.appendRow(new)
    
"""Container class for all data"""
class AppState:
    columnsHeadersExternal = ["Temperature (K)","Magnetic Field (Oe)","AC X' (emu/Oe)","AC X'' (emu/Oe)","AC Frequency (Hz)"]
    epsTemp = 0.05
    epsField = 1
    def __init__(self, mainPage):
        self.ui = mainPage
        self.whole = RootItem(self.ui, 'Main')
        
 
    def addModel(self, name):
        if name in self.models:
            print("Model already exists choose other name or delete old one!")
            return
        self.models[name] = ModelItem(self.ui, name)