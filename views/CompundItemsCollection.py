from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu, QFileDialog, QWidget, QMessageBox

from models import CompoundItemsCollectionModel, Compound 
from controllers import CompoundItemsCollectionController, CompoundItemController

from .StandardItem import StandardItem
from .CompoundItem import CompoundItem

from protocols import Collection
from os import path
from json import load, dump
from typing import cast 

class CompoundItemsCollection(StandardItem):

    def __init__(self, model: CompoundItemsCollectionModel, ctrl: CompoundItemsCollectionController):
        super().__init__(model._name, model._font_size, model._set_bold)
        self.setBackground(QBrush(QColor(255,122,0)))
        self._model: CompoundItemsCollectionModel = model
        self._ctrl: CompoundItemsCollectionController = ctrl
        self._model.compound_added.connect(self.on_compound_added)
        self._model.compound_removed.connect(self.on_compound_removed)
        self.save_filename: str|None = None

    def on_click(self):
        self._ctrl.display()

    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def on_compound_added(self, new:Compound):
        cmp: CompoundItem = CompoundItem(new, CompoundItemController(new))
        self.appendRow(cmp)
        self._model._tree.expandAll()
        

    def on_compound_removed(self, index:QModelIndex):
        self.removeRow(index.row())

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Create new compound", self._ctrl.add_compound)  
        menu.addAction("Load compounds from .json file", self.load_from_json)
        menu.addAction("Save compounds to .json file", self.save_to_json)  
        menu.exec(menu_position)

    def load_from_json(self):
        dlg: QFileDialog = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)

        if dlg.exec():
           filenames = dlg.selectedFiles()
        else:
           return

        if len(filenames) != 1 :
            return 

        filepath = filenames[0]  
        if not path.isfile(filepath):
            print("File path {} does not exist. Exiting...".format(filepath))
            return

        with open(filepath, "r") as f:
            jsonable = load(f)

        if jsonable["version"] == "2.1":
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Chosen file is corrupted!")
            msg.setWindowTitle("Loading from .json file stoped.")
            msg.exec()
            return

        self.from_json(jsonable)

    def from_json(self, json: dict):
        names_to_skip: set[str] = set()
        for compound in json["compounds"]:
            try:
                self._model.append_existing_compound(Compound(compound["name"], compound["molar_mass"], cast(Collection, self._model), self._model._tree, self._model._displayer))
            except ValueError as e:
                names_to_skip.add(compound["name"])
                print(e)
                print("Loading skipped")

        i: int = 0
        nr_of_rows: int = self.rowCount()
        while i < nr_of_rows:
            compound_item: CompoundItem = cast(CompoundItem, self.child(i))
            compound_json = json["compounds"][i]

            if compound_json["name"] not in names_to_skip:
                compound_item.m_model.from_json(compound_json["measurements"])
                compound_item.f1_model.from_json(compound_json["f1_fits"])
                compound_item.f2_model.from_json(compound_json["f2_fits"])
                compound_item.t_model.from_json(compound_json["tau_fits"])

            i = i + 1

    def save_to_json(self):
        name: str = QFileDialog.getSaveFileName(QWidget(), 'Save file')
        if name == "":
            return

        compounds: list[dict] = []
        i: int = 0
        nr_of_rows: int = self.rowCount()
        while i < nr_of_rows:
            compound_item: CompoundItem = cast(CompoundItem, self.child(i))
            jsonable: dict = compound_item._model.get_jsonable()
            jsonable.update({"measurements": compound_item.m_model.get_jsonable()})
            jsonable.update({"f1_fits": compound_item.f1_model.get_jsonable()})
            jsonable.update({"f2_fits": compound_item.f2_model.get_jsonable()})
            jsonable.update({"tau_fits": compound_item.t_model.get_jsonable()})
            compounds.append(jsonable)
            i = i + 1

        jsonable = {"version": 2.1, "compounds": compounds}
        self.save_filename = name[0] + '.json' if len(name[0].split('.')) == 1 else name[0][:-5] + '.json'
        with  open(self.save_filename, 'w') as f:
            dump(jsonable, f, indent=4)

    def save(self):
        print(self.save_filename)
        if self.save_filename is None or self.save_filename == "" or self.save_filename == ".json":
            self.save_to_json()
        else:
            compounds: list[dict] = []
            i: int = 0
            nr_of_rows: int = self.rowCount()
            while i < nr_of_rows:
                compound_item: CompoundItem = cast(CompoundItem, self.child(i))
                jsonable: dict = compound_item._model.get_jsonable()
                jsonable.update({"measurements": compound_item.m_model.get_jsonable()})
                jsonable.update({"f1_fits": compound_item.f1_model.get_jsonable()})
                jsonable.update({"f2_fits": compound_item.f2_model.get_jsonable()})
                jsonable.update({"tau_fits": compound_item.t_model.get_jsonable()})
                compounds.append(jsonable)
                i = i + 1

            jsonable = {"version": 2.1, "compounds": compounds}
            try:
                with  open(self.save_filename, 'w') as f:
                    dump(jsonable, f, indent=4)
            except Exception as e:
                self.save_to_json()
