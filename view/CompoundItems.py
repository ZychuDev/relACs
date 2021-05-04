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
        name, status = QtWidgets.QInputDialog.getText(self.ui.window, "Compund Creation",
        "Enter name for new compound:")
        if status == True:
            if name in self.container:
                #TO DO: Ui information
                print("Compound already exists choose other name or delete old one!")
                return False #To DO throw exception
        molar_mass, status = QtWidgets.QInputDialog.getDouble(self.ui.window, 'Compund Creation', 'Enter molar mass:', decimals=6)
        if status == True:
            new = CompoundItem(self.ui, name, molarMass= molar_mass)
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
    
