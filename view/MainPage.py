from tkinter import Scrollbar
from .Plot import Plot
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont, QColor
from PyQt5.QtWidgets import QFileDialog, QGraphicsSceneResizeEvent, QPushButton, QMenu
from PyQt5.QtCore import QFile, Qt

from .MainPageUI2 import *
#from .Fit2D import Fit2D

import sys
import os

import pandas as pd
import numpy as np

class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__()
        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        #self.setIcon(toSuka.png)
    def action(self):
        print("No provided action for this item")


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
        result.df = df
        return result

    def action(self):
        print("Clicked Data Item")

    def showMenu(self, position):
        return

class DataCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, point):
        menu = QMenu()
        load = menu.addAction("Load from file1", self.loadFromFile)

        action = menu.exec_(self.ui.window.mapToGlobal(point))


    def loadFromFile(self):
        # TO DO: implement more complex custom dialog file
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
        else:
            return

        if len(filenames) != 1 :
             return 

        filepath = filenames[0]
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

        










class FitFrequencyItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

class FitFrequencyCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.mainPage = mainPage
        self.markColor = QColor(46,184,199)
        #self.setBackground(markColor)


    def action(self):
        self.mainPage.plot1.change()
        self.mainPage.plot2.change()
        self.mainPage.plotMain.change()

        width = self.mainPage.WorkingSpace.frameGeometry().width()
        height = self.mainPage.WorkingSpace.frameGeometry().height()
        self.mainPage.WorkingSpace.adjustSize()
        self.mainPage.WorkingSpace.resize(width, height)
    
    def showMenu(self, point):
        menu = QMenu()
        inspect = menu.addAction("Inspect", self.action)
        action = menu.exec_(self.mainPage.window.mapToGlobal(point))
        if action == inspect:
            self.action()





class FitTauItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)

    


class FitTauCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        button = QPushButton("Whatever")
        button.clicked.connect(self.action)
        mainPage.LeftPanel.insertWidget(0, button )
        mainPage.RightPanel.insertWidget(0, Plot(caption='3D WooDoo'))

    def action(self):
        print(1)
        self.mainPage.WorkingSpace.setCurrentWidget(self.mainPage.fit2Dpage)

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
    
    def showMenu(self, point):
        menu = QMenu()
        new = menu.addAction("New", self.action)
        action = menu.exec_(self.ui.window.mapToGlobal(point))
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

    def showMenu(self, point):
        pass




class RootItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=16, set_bold=True, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.compounds = CompoundCollectionItem(self.ui, "Compounds")
        self.models = ModelCollectionItem(self.ui, "Models")

        self.appendRow(self.compounds)
        self.appendRow(self.models)

    def showMenu(self, point):
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





        

class MainPage(Ui_MainWindow):

    def __init__ (self, window):
        super().__init__()
        self.setupUi(window)
        self.appState = AppState(self)
        self.window = window
        #self.window.showMaximized()

        button = QPushButton("Whatever")
        button.clicked.connect(lambda x:self.WorkingSpace.setCurrentWidget(self.fit2Dpage))
        self.LeftPanel.insertWidget(0, button )

        self.RightPanel.insertWidget(0, Plot(caption='3D WooDoo'))
        self.WorkingSpace.setCurrentWidget(self.fit2Dpage)
        self.Model.setRootIsDecorated(False)
        self.Model.setAlternatingRowColors(True)
        self.Model.setHeaderHidden(True)
        

        self.Model.doubleClicked.connect(self.getValue)

        self.Model.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Model.customContextMenuRequested.connect(self.showMenu)

        self.treeModel = QStandardItemModel()
        

 
        rootNode = self.treeModel.invisibleRootItem()

        chlor = CompoundItem(self, "Chlor")
        self.appState.whole.compounds.append(chlor)
#   ------Test Structure------
        # data = DataCollectionItem(self, 'Data')
        # FrequencyFits = FitFrequencyCollectionItem(self, 'FrequencyFits(2D)')
        # TauFits = FitTauCollectionItem(self, 'TauFits(3D)')

        # chlor.appendRow(data)
        # chlor.appendRow(FrequencyFits)
        # chlor.appendRow(TauFits)

        # record = FitFrequencyItem(self, 'Temp: 5, Field: 180')
        # record1 = StandardItem('Temp: 3, Field: 180', 12)
        # record2 = StandardItem('Temp: 5, Field: 181', 12)

        # data.appendRow(record)
        # data.appendRow(record1)
        # data.appendRow(record2)
        

        rootNode.appendRow(self.appState.whole)

        self.Model.setModel(self.treeModel)
        self.Model.setColumnWidth(0,250)
        self.Model.expandAll()

        
        

        
        """Workspace implementation"""
        
        self.plot1 = Plot(caption='Pierwszy')
        self.plot2 = Plot(caption='Drugi')
        self.plotMain = Plot(caption="Główny")

        self.UpperPlots.insertWidget(0, self.plot1)
        self.UpperPlots.insertWidget(1, self.plot2)
        self.MainPlot.insertWidget(3, self.plotMain)

        button = QPushButton('Change')
        button.clicked.connect(self.change)

        # buttonNext = QPushButton('Next')
        # buttonNext.clicked.connect(self.nextWidget)

        self.BottomPanel.addWidget(button)
        # self.horizontalLayout.addWidget(buttonPrevious)



    def getValue(self, val):
        self.treeModel.itemFromIndex(val).action()

    def showMenu(self, point):
        index = self.Model.indexAt(point)
        self.treeModel.itemFromIndex(index).showMenu(point)

    def nextWidget(self):
        self.WorkingSpace.setCurrentIndex((self.WorkingSpace.currentIndex() + 1) % 3)
        print(self.WorkingSpace.currentIndex())

    def previousWidget(self):
        self.WorkingSpace.setCurrentIndex((self.WorkingSpace.currentIndex() - 1) % 3)
        print(self.WorkingSpace.currentIndex())
    
    def change(self):
        self.plot1.change('ABC')
        print(self.UpperPlots.indexOf(self.plot1))
        width = self.WorkingSpace.frameGeometry().width()
        height = self.WorkingSpace.frameGeometry().height()
        self.WorkingSpace.adjustSize()
        self.WorkingSpace.resize(width, height)

        
    


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










