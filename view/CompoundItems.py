from .StandardItem import StandardItem

from PyQt5.QtGui import QColor, QDoubleValidator
from PyQt5.QtWidgets import QLabel, QMenu, QVBoxLayout, QLineEdit
from PyQt5.QtCore import QSize, Qt

from .TauItems import *
from .DataItems import *
from .FrequencyItems import *
from .Modeltems import *

import json
import configparser

class CompoundCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=14, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.container = {}
    
    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("New", self.add)
        menu.addAction("Save", self.save_to_json)
        menu.addAction("Load", self.load_from_json)
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
        dialog.setLabelText('Enter molar mass in g/mol:')
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

    def save_to_json(self, file_name=None):
        if file_name is None:
            file_name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')
        try:
            with  open(file_name[0], 'w') as f:
                #or make custom encoder and decoder
                data = self.to_json()
                json.dump(data, f, indent=4)
        except Exception as e:
            print(e)
            return

    def load_from_json(self, file_name=None):
        if file_name is None:
            file_name = QtWidgets.QFileDialog.getOpenFileName(self.ui.window, 'Load from file')
        try:
            with open(file_name[0], 'r') as f:
                compounds = json.load(f)
                self.from_json(compounds)
        except Exception as e:
            print(e)
            return

    def from_json(self, compounds):
        self.removeRows(0, self.rowCount())
        self.container = {}
        for key in compounds:
            self.append(self.compund_item_from_json(compounds[key]))
        return

    def to_json(self):
        return " "

    def compound_item_from_json(self, compound):
        new = CompoundItem()
        return new

                

class CompoundItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0),
    molar_mass = 2000):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage

        self.name = txt
        self.molar_mass = molar_mass #TO DO: implement dialog box option for it

        config = configparser.RawConfigParser()
        config.optionxform = str

        config.read('view/default_settings.ini')
        r = config['Ranges']
        self.ranges = {}
        for p in r:
            self.ranges[p] = [float(s) for s in config['Ranges'][p].split(',')]
        print(f"Ranges{self.ranges}")
        self.log_params = ('Adir', 'B1', 'B2', 'B3', 'Tau0')


        self.data = DataCollectionItem(self.ui, 'Data')
        self.FrequencyFits = FitFrequencyCollectionItem(self.ui, 'Frequency Fits Single Relaxation')
        self.FrequencyFits2 = FitFrequencyCollectionItem(self.ui, 'Frequency Fits Double Relaxations', 2)
        self.TauFits = FitTauCollectionItem(self.ui, 'TauFits(3D)')

        self.appendRow(self.data)
        self.appendRow(self.FrequencyFits)
        self.appendRow(self.FrequencyFits2)
        self.appendRow(self.TauFits)

    def addTo(self, collection):
        collection.appendRow(self)
        

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Change Ranges", self.change_ranges)
        menu.exec_(self.ui.window.mapToGlobal(position))

    def change_ranges(self, return_to=None):
        dlg = QDialog()
        dlg.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        dlg.setWindowTitle("Set parameters ranges")
        layout = QVBoxLayout()
        new_ranges = {}
        for p in self.ranges:
            l = QHBoxLayout()
            low = QLineEdit()
            low.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

            v = QDoubleValidator()
            loc = QLocale(QLocale.c())
            loc.setNumberOptions(QLocale.RejectGroupSeparator)
            v.setLocale(loc)

            low.setValidator(v)
            low.setText(str(self.ranges[p][0]))

            up = QLineEdit()
            up.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))


            up.setValidator(v)
            up.setText(str(self.ranges[p][1]))

            new_ranges[p] = [low, up]
            l.addWidget(low)
            label = QLabel(p)
            label.setMinimumSize(QSize(65, 0))
            label.setAlignment(Qt.AlignCenter)
            l.addWidget(label)
            l.addWidget(up)
            layout.addLayout(l)
        l = QHBoxLayout()
        button = QPushButton("Apply")
        button.clicked.connect(partial(self.set_new_ranges, new_ranges, False, dlg, return_to))

        button2 = QPushButton("Force change")
        button2.clicked.connect(partial(self.set_new_ranges, new_ranges, True, dlg, return_to))
        l.addWidget(button)
        l.addWidget(button2)
        layout.addLayout(l)
        dlg.setLayout(layout)
        dlg.exec_()

    def set_new_ranges(self, edit_lines, force, dlg, return_to=None):
        for p in edit_lines:
            if float(edit_lines[p][0].text()) >=  float(edit_lines[p][1].text()):
                message = str("Each upper bound must be strictly greater than lower bound\n"
                 + f"Bounds for parameter: {p} are invalid")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(message)
                msg.setWindowTitle("Incorrect bounds")
                msg.exec_()
                return
        
        for p in edit_lines:
            lower = float(edit_lines[p][0].text())
            upper = float(edit_lines[p][1].text())

            if not force:
                for j in [1,2,3]:
                    collection = self.child(j)
                    if j != 3:
                        i = 0
                        while collection.child(i) is not None:
                            for r in collection.child(i).relaxations:
                                if p not in list(r.previous.keys()):
                                    i += 1
                                    continue
                                if r.previous[p] < lower or r.previous[p] > upper:
                                    message = str(f"Bounds for parameter: {p} are invalid\n"
                                    +f"In {collection.child(i).name} saved value of paramater is not in given range\n"
                                    +"Force new ranges or change saved values of the parameters")
                                    msg = QMessageBox()
                                    msg.setIcon(QMessageBox.Warning)
                                    msg.setText(message)
                                    msg.setWindowTitle("Incorrect bounds")
                                    msg.exec_()
                                    return
                            i += 1
                    else:
                        i = 0
                        while collection.child(i) is not None:
                            if p not in collection.child(i).previous.keys():
                                i += 1
                                continue
                            if collection.child(i).previous[p] < lower or collection.child(i).previous[p] > upper:
                                        message = str(f"Bounds for parameter: {p} are invalid\n"
                                        +f"In {collection.child(i).name} saved value of paramater is not in given range\n"
                                        +"Force new ranges or change saved values of the parameters")
                                        msg = QMessageBox()
                                        msg.setIcon(QMessageBox.Warning)
                                        msg.setText(message)
                                        msg.setWindowTitle("Incorrect bounds")
                                        msg.exec_()
                                        return
                                        
                            i += 1
            QApplication.setOverrideCursor(Qt.WaitCursor)
            QApplication.processEvents()
            self.ranges[p] = [lower, upper]
            for j in [1,2,3]:
                collection = self.child(j)
                if j != 3:
                    i = 0
                    while collection.child(i) is not None:
                        if j != 3:
                            for r in collection.child(i).relaxations:
                                if p not in list(r.previous.keys()):
                                    continue
                                if r.previous[p] < lower:
                                    r.previous[p] = np.nextafter(lower, upper)
                                    r.current[p] = r.previous[p]
                                if r.previous[p] > upper:
                                    r.previous[p] = np.nextafter(upper, lower)
                                    r.current[p] = r.previous[p]
                        else:
                            r = collection.child(i)
                            if p not in list(r.previous.keys()):
                                continue
                            if r.previous[p] < lower:
                                r.previous[p] = np.nextafter(lower, upper)
                                r.current[p] = r.previous[p]
                            if r.previous[p] > upper:
                                r.previous[p] = np.nextafter(upper, lower)
                                r.current[p] = r.previous[p]
                        i += 1
            QApplication.restoreOverrideCursor()
            QApplication.processEvents()
            if return_to is not None:
                return_to()
            else:
                self.ui.WorkingSpace.setCurrentWidget(self.ui.homePage)
            dlg.accept()









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
    
