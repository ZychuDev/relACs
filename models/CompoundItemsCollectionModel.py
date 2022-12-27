from .Compound import Compound
from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTreeView

from protocols import Displayer, Collection

from typing import cast 

class CompoundItemsCollectionModel(QObject):
    name_changed: pyqtSignal = pyqtSignal(str)
    compound_added: pyqtSignal = pyqtSignal(Compound)
    compound_removed: pyqtSignal = pyqtSignal(QModelIndex)

    def __init__(self, name:str, tree:QTreeView, displayer: Displayer):
        """Agregate Compounds

        Args:
            name (str): Collection name
            tree (QTreeView): Control tree reference.
            displayer (Displayer): Object responsible for visualization.

        Attributes:
            name_changed: Emitted when collection name is changed. Contains new name.
            compound_added: Emitted when new Compound is added to collection. Contains new Compound.
            compound_removed: Emitted when Compound is removed from collection. Contains Compound's Index in controll tree.
        """
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
        """Create and adds new compund to collection.

        Args:
            name (str): Name of the compound to create.
            molar_mass (float): Moalr mass in g/mol.

        Raises:
            ValueError: Raised when Compound with given name already exists in collection.
        """
        if name in self._names:
            raise ValueError(f"Compund with name {name} already exist in this collection")
        
        new: Compound = Compound(name, molar_mass, cast(Collection, self) ,self._tree, self._displayer)
        self._compounds.append(new)
        self._names.add(name)
        self.compound_added.emit(new)
        
    def append_existing_compound(self, compound: Compound):
        """Adds Compound to colection.

        Args:
            compound (Compound): Compound to add to collection.

        Raises:
            ValueError: Raised when Compound with the same name already exists in collection.
        """
        if compound._name in self._names:
            raise ValueError(f"Compound with name {compound._name} already exist in this collection")

        self._compounds.append(compound)
        self._names.add(compound._name)
        self.compound_added.emit(compound)

                
    def create_compound_from_json(self, json: dict) -> Compound:
        """Create compound from json.

        Args:
            json (dict): Result of get_jsonable().

        Returns:
            Compound: Recreated compund from json.
        """
        new_model: Compound = Compound(json["name"], json["molar_mass"], cast(Collection, self), self._tree, self._displayer)
        return new_model
    
    def remove(self, compound_name:str, index: QModelIndex):
        """Remove compound with given name. Emits it's index in cotroll tree.

        Args:
            compound_name (str): Name of the Compund to remove.
            index (QModelIndex): It's index in controll tree.
        """
        if compound_name in self._names:
            self._names.remove(compound_name)
            self._compounds = [compound for compound in self._compounds if (compound.name in self._names)]
            self.compound_removed.emit(index)

    def check_name(self, name: str) -> bool:
        """Check if Compound with given name is already in collection.

        Args:
            name (str): Compound name.

        Returns:
            bool: If name is already taken.
        """
        return name in self._names
    
    def update_names(self, old_name: str, new_name: str):
        """Updates name register in collection.

        Args:
            old_name (str): Old Compound name.
            new_name (str): New Compound name.
        """
        self._names.remove(old_name)
        self._names.add(new_name)

    def change_displayed_item(self, name: str):
        pass

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        """Checks Compound select state.

        Args:
            index (QModelIndex): Compound index in cotroll tree.

        Returns:
            bool: Check state.
        """
        selected: list[QModelIndex] = self._tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False





    