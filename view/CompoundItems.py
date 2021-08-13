from .StandardItem import StandardItem

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu

from .TauItems import *
from .DataItems import *
from .FrequencyItems import *
from .Modeltems import *

class CompoundCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=14, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.container = {}
    
    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("New", self.add)
        menu.exec_(self.ui.window.mapToGlobal(position))


    def add(self):
        #name, status = QtWidgets.QInputDialog.getText(self.ui.window, "Compund Creation",
        #"Enter name for new compound:")
        name, ok = QInputDialog.getText(self.ui.window, 'Creating new compund', 'Enter name of compound:')
        if ok:
            if name in self.container:
                #TO DO: Ui information
                print("Compound already exists choose other name or delete old one!")
                return False #To DO throw exception
        #molar_mass, status = QtWidgets.QInputDialog.getDouble(self.ui.window, 'Compund Creation', 'Enter molar mass:', decimals=6, min = 0.0)
        dialog = QInputDialog()
        dialog.setInputMode(QInputDialog.DoubleInput)
        dialog.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        dialog.setLabelText('Enter molar mass:')
        dialog.setDoubleMinimum(0.0)
        dialog.setDoubleMaximum(1000000.0)
        dialog.setDoubleDecimals(6)
        dialog.setWindowTitle('Compound Creation')
        status = dialog.exec_()
        # molar_mass = 1000
        if status == True:
            molar_mass = dialog.doubleValue()
            new = CompoundItem(self.ui, name, molar_mass= molar_mass)
            self.appendRow(new)
            self.ui.TModel.expandAll()
            self.container[name] = new

    def append(self, compound):
        if compound.name in self.container:
            #TO DO: Ui information
            print("Compound already exists choose other name or delete old one!")
            return False #To DO throw exception
        self.appendRow(compound)
        self.ui.TModel.expandAll()
        self.container[compound.name] = compound

                

class CompoundItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0),
    molar_mass = 2000):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.name = txt
        self.molar_mass = molar_mass #TO DO: implement dialog box option for it

        self.data = DataCollectionItem(self.ui, 'Data')
        self.FrequencyFits = FitFrequencyCollectionItem(self.ui, 'Frequency Fits Single Relaxation')
        self.FrequencyFits2 = FitFrequencyCollectionItem(self.ui, 'Frequency Fits Double Relaxations')
        self.TauFits = FitTauCollectionItem(self.ui, 'TauFits(3D)')

        self.appendRow(self.data)
        self.appendRow(self.FrequencyFits)
        self.appendRow(self.FrequencyFits2)
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
        
        self.appendRow(self.compounds)
        

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
    
