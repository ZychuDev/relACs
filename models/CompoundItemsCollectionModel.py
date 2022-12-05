from .Compound import Compound
from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QTreeView

from protocols import Displayer

class CompoundItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    compound_added = pyqtSignal(Compound)
    compound_removed = pyqtSignal(QModelIndex)

    def __init__(self, name:str, tree:QTreeView, displayer: Displayer):
        super().__init__()
        self._name: str = name

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._compounds: list[Compound] = []
        self._names: set[str] = set()

        self._tree: QTreeView = tree
        self._displayer = displayer

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Measurement name must be at least one character long")
        self._name = val
        self.name_changed.emit(val)
        
    def append_new_compound(self, name: str, molar_mass: float):
        if name in self._names:
            raise ValueError(f"Compund with name {name} already exist in this collection")
        
        new: Compound = Compound(name, molar_mass, self ,self._tree, self._displayer)
        self._compounds.append(new)
        self._names.add(name)
        self.compound_added.emit(new)
        
    def append_existing_compound(self, compound: Compound):
        if compound._name in self._names:
            raise ValueError(f"Compund with name {compound._name} already exist in this collection")

        self._compounds.append(compound)
        self._names.add(compound._name)
        self.compound_added.emit(compound)

                
    
    def create_compound_from_json(self, json):
        new_model: Compound = Compound(json["name"], json["molar_mass"], self, self._tree, self._displayer)
        return new_model

        self.append_existing_compound(new_model)
    
    def remove(self, compound_name:str, index: QModelIndex):
        if compound_name in self._names:
            self._names.remove(compound_name)
            self._compounds = [compound for compound in self._compounds if (compound.name in self._names)]
            self.compound_removed.emit(index)

    def check_name(self, name: str) -> bool:
        return name in self._names
    
    def update_names(self, old_name: str, new_name: str):
        self._names.remove(old_name)
        self._names.add(new_name)

    def change_displayed_item(self, name: str):
        pass

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        selected: list[QModelIndex] = self._tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False





    