from .Compound import Compound
from .Fit import Fit
from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush

from protocols import Collection
from typing import cast

from pandas import read_json # type: ignore

class FitItemsCollectionModel(QObject):
    name_changed: pyqtSignal = pyqtSignal(str)
    fit_added: pyqtSignal = pyqtSignal(Fit)
    fit_removed: pyqtSignal = pyqtSignal(QModelIndex)
    displayed_item_changed: pyqtSignal = pyqtSignal(Fit)
    
    """Aggregation of fits

    Args:
        name (str): Name of collection.
        compound (Compound): Parent.

    Attributes:
        name_changed: Emitted when collection name is changed. Contains new name.
        fit_added: Emitted when new fit is added to collection. Contains new Fit.
        fit_removed: Emitted when fit is removed from collection. Contains Fit's Index in controll tree. 
        displayed_item_change: Emitted when displayed fit is replaced.
    """

    def __init__(self, name: str, compound: Compound):
        super().__init__()
        self._name: str = name
        self._compound: Compound = compound

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._fits: list[Fit] = []
        self._names: set[str] = set()

        self._displayed_item: Fit

    @property
    def tree(self):
        return self._compound._tree

    @property
    def name(self):
        return self._name

  
    @name.setter
    def name(self, val: str):
        if len(val) < 1:
            raise ValueError("Measurement name must be at least one character long")

        self._name = val
        self.name_changed.emit(val)
        
    def append_fit(self, fit: Fit, silent: bool=False, display: bool=False):
        """Apped Fit to collection

        Args:
            fit (Fit): Fit to add to collection 
            silent (bool, optional): Determines whether fit_added signal will be emitted. Defaults to False.
            display (bool, optional): Determines whether display newly added Fit. Defaults to False.
        """
        if fit.name in self._names:
            print(f"Fit with name {fit.name} already exists.\n Loading skipped")
            return

        self._fits.append(fit)
        self._names.add(fit.name)
        fit._collection = cast(Collection, self)
        if not silent:
            self.fit_added.emit(fit)
        if display:
            self.change_displayed_item(fit.name)

    def remove(self, fit_name: str, index: QModelIndex):
        """Remove Fit with given name from collection.

        Args:
            fit_name (str): Name of Fit to remove.
            index (QModelIndex): Fit's index in controll tree.
        """
        if fit_name in self._names:
            self._names.remove(fit_name)
            self._fits = [fit for fit in self._fits if fit.name in self._names]
            self.fit_removed.emit(index)

    def check_name(self, name: str) -> bool:
        """Check if Fit with given name is already in collection.

        Args:
            name (str): Fit name.

        Returns:
            bool: If name is already taken.
        """
        return name in self._names

    def update_names(self, old_name: str, new_name: str):
        """Updates name register in collection.

        Args:
            old_name (str): Old Fit name.
            new_name (str): New Fit name.
        """
        self._names.remove(old_name)
        self._names.add(new_name)

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        """Checks Fit select state.

        Args:
            index (QModelIndex): Fit Index in cotroll tree.

        Returns:
            bool: Check state.
        """
        selected: list[QModelIndex] = self.tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False

    def change_displayed_item(self, name: str):
        """Replace currently displayed fit.

        Args:
            name (str): Name of the Fit to display.
        """
        new_item: Fit = next(fit for fit in self._fits if fit.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)

    def get_next(self, name: str) -> str:
        """Get name of next Fit in collection.

        Args:
            name (str): Current Fit name.

        Returns:
            str: Next Fit name.
        """
        for i, f in enumerate(self._fits):
            if f.name == name:
                break

        if i == len(self._fits)-1:
            return self._fits[0].name
        else:
            return self._fits[i+1].name

    def get_previous(self, name: str) -> str:
        """Get name of previous Fit in collection.

        Args:
            name (str): Current Fit name.

        Returns:
            str: Previous Fit name.
        """
        for i, f in enumerate(self._fits):
            if f.name == name:
                break

        if i == 0:
            return self._fits[-1].name
        else:
            return self._fits[i-1].name

    def get_item_model(self, name: str) -> Fit|None:
        """Get Fit of given name

        Args:
            name (str): Name of Fit to retrive.

        Returns:
            Fit | None: Fit with given name or None if it is not part of collection.
        """
        for f in self._fits:
            if f.name == name:
                return f
        else:
            return None

    def get_names(self) -> set[str]: 
        """Get register of names

        Returns:
            set[str]: All names of collection elements.
        """
        return self._names
    
    def get_jsonable(self) -> list[dict]:
        """Marshal collection to python list of dictionaries.

        Returns:
            list[dict]: All Fits in collection marshaled into dictionaries.
        """
        jsonable: list = [fit.get_jsonable() for fit in self._fits]
        return jsonable

    def from_json(self, fits: list[dict]):
        """Append new Fits created from result of get_jsonable()"""
        for f in fits:
            new_model = Fit(f["name"], read_json(f["df"]), f["tmp"], f["field"], self._compound, cast(Collection, self))
            new_model.update_relaxations_from_json(f["relaxations"])
            self.append_fit(new_model)