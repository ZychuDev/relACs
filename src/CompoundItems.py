from .StandardItem import StandardItem

from PyQt5.QtGui import QColor, QDoubleValidator, QBrush
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
        self.setBackground(QBrush(QColor(255,144,40)))
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
            new = CompoundItem(self.ui, txt=name, molar_mass= molar_mass)
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

        self.from_json(jsonable)


    def create_from_json(self, jsonable):
        compound_item = CompoundItem(self.ui, full=False)
        compound_item.from_json(jsonable)
        i = 2
        if compound_item.name in self.container:
            saved_name = compound_item.name
            compound_item.name = saved_name + f"_{i}"
        while(compound_item.name in self.container):
            i += 1
            compound_item.name = saved_name + f"_{i}"

        compound_item.setText(compound_item.name)
        return compound_item

    def get_jsonable(self):
        items_list = []
        i = 0
        while(self.child(i) != None):
            items_list.append(self.child(i).get_jsonable())
            i += 1
        jsonable = {'items_list':items_list}
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
            compund_item = self.create_from_json(item)
            self.append(compund_item)
        

                

class CompoundItem(StandardItem):
    def __init__(self, mainPage,full=True, txt='', font_size=12, set_bold=False, color=QColor(0,0,0),
    molar_mass = 2000):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        # self.setBackground(QBrush(QColor(0,255,0)))
        self.name = txt
        self.molar_mass = molar_mass #TO DO: implement dialog box option for it

        config = configparser.RawConfigParser()
        config.optionxform = str

        config.read('settings/default_settings.ini')
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

        if full:
            self.appendRow(self.data)
            self.appendRow(self.FrequencyFits)
            self.appendRow(self.FrequencyFits2)
            self.appendRow(self.TauFits)

    def get_jsonable(self):
        jsonable = {'name': self.name, 'ranges': self.ranges, 'log_params':self.log_params, 'data':self.data.get_jsonable(),
         'frequency_fits': self.FrequencyFits.get_jsonable(), 'frequency_fits_2': self.FrequencyFits2.get_jsonable(),
         'tau_fits': self.TauFits.get_jsonable()}
        return jsonable

    def from_json(self, json):
        self.name = json['name']
        self.ranges = json['ranges']
        self.log_params = json['log_params']

        data_collection = DataCollectionItem(self.ui, 'Data')
        self.appendRow(data_collection)
        data_collection.from_json(json['data'])
        self.data = data_collection

        frequency_collection_1 = FitFrequencyCollectionItem(self.ui, 'Frequency Fits Single Relaxation')
        self.appendRow(frequency_collection_1)
        frequency_collection_1.from_json(json['frequency_fits'])
        self.FrequencyFits = frequency_collection_1

        frequency_collection_2 = FitFrequencyCollectionItem(self.ui, 'Frequency Fits Double Relaxations', 2)
        self.appendRow(frequency_collection_2)
        frequency_collection_2.from_json(json['frequency_fits_2'])
        self.FrequencyFits2 = frequency_collection_2

        tau_collection = FitTauCollectionItem(self.ui, 'TauFits(3D)') 
        self.appendRow(tau_collection)
        tau_collection.from_json(json['tau_fits'])
        self.TauFits = tau_collection

    def addTo(self, collection):
        collection.appendRow(self)
        

    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Change Ranges", self.change_ranges)
        menu.addAction("Remove", self.remove)
        menu.exec_(self.ui.window.mapToGlobal(position))

    def remove(self):
        self.parent().container.pop(self.name, None)
        self.parent().removeRow(self.index().row())

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
            print(p)
            label_txt = p if p != 'chiT' else 'chiT-chiS'
            label = QLabel(label_txt)
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
                                     +f"Lower : {lower}\n Upper: {upper}\n Actual: {r.previous[p]}" 
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
                            if (collection.child(i).previous[p] < (lower if p not in collection.parent().log_params else 10**lower) 
                            or collection.child(i).previous[p] > (upper if p not in collection.parent().log_params else 10**upper)):
                                        message = str(f"Bounds for parameter: {p} are invalid\n"
                                         +f"In {collection.child(i).name} saved value of paramater is not in given range\n"
                                         +f"Lower : {lower if p not in collection.parent().log_params else 10**lower} "
                                         +f"Upper: {upper if p not in collection.parent().log_params else 10**upper} "
                                         +f"Actual: {collection.child(i).previous[p]}\n" 
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
        self.setBackground(QBrush(QColor(255,122,0)))
        self.ui = mainPage

        self.compounds = CompoundCollectionItem(self.ui, "Compounds")
        
        self.appendRow(self.compounds)

    def double_click(self):
        self.click()

    def click(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.homePage)
        

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
    
