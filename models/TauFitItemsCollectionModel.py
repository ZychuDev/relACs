from .Compound import Compound
from .TauFit import TauFit

from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor

from protocols import Collection
from typing import cast

class TauFitItemsCollectionModel(QObject):
    """_summary_

        Args:
            name (str): Name of collection.
            compound (Compound): The Compound to which it belongs.

        Attributes:
            name_changed: Emitted when collection name is changed. Contains new name.
            fit_added: Emitted when new TauFit is added to collection. Contains new TauFit.
            fit_removed: Emitted when TauFit is removed from collection. Contains removed TauFit's Index in controll tree. 
            displayed_item_changed: Emitted when displayed TauFit is replaced.
    """

    name_changed: pyqtSignal = pyqtSignal(str)
    fit_added: pyqtSignal = pyqtSignal(TauFit)
    fit_removed: pyqtSignal = pyqtSignal(QModelIndex)
    displayed_item_changed: pyqtSignal = pyqtSignal(TauFit)

    def __init__(self, name:str, compound: Compound):

        super().__init__()
        self._name: str = name
        self._compound: Compound = compound

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._tau_fits: list[TauFit] = []
        self._names: set[str] = set()

        self._displayed_item: TauFit

    @property
    def tree(self):
        return self._compound._tree

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name:str):
        self._name = new_name
        self.name_changed.emit(new_name)
        

    def remove(self, tau_fit_name: str, index: QModelIndex):
        """Remove TauFit with given name from collection.

        Args:
            tau_fit_name (str): Name of TauFit to remove.
            index (QModelIndex): Removed TauFit's index in controll tree.
        """
        if tau_fit_name in self._names:
            self._names.remove(tau_fit_name)
            self._tau_fits = [fit for fit in self._tau_fits if fit.name in self._names]
            self.fit_removed.emit(index)

    def update_names(self, old_name: str, new_name: str):
        """Updates name register in collection.

        Args:
            old_name (str): Old TauFit name.
            new_name (str): New TauFit name.
        """
        self._names.remove(old_name)
        self._names.add(new_name)

    def check_name(self, name: str) -> bool:
        """Check if TauFit with given name is already in collection.

        Args:
            name (str): TauFit name.

        Returns:
            bool: If name is already taken.
        """

        return name in self._names

    def change_displayed_item(self, name: str):
        """Replace currently displayed TauFit.

        Args:
            name (str): Name of the TauFit to display.
        """
        new_item: TauFit = next(fit for fit in self._tau_fits if fit.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)

    def append_tau_fit(self, fit: TauFit, silent: bool=False, display: bool=False):
        """Apped tauFit to collection

        Args:
            Taufit (Fit): TauFit to add to collection 
            silent (bool, optional): Determines whether fit_added signal will be emitted. Defaults to False.
            display (bool, optional): Determines whether display newly added Fit. Defaults to False.
        """
        if fit.name in self._names:
            print(f"Tau fit with name {fit.name} already exists.\n Loading skipped")
            return

        self._tau_fits.append(fit)
        self._names.add(fit.name)
        fit._collection = cast(Collection, self)
        if not silent:
            self.fit_added.emit(fit)
        if display:
            self.change_displayed_item(fit.name)

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        """Checks tauFit select state.

        Args:
            index (QModelIndex): TauFit Index in cotroll tree.

        Returns:
            bool: Check state.
        """
        selected: list[QModelIndex] = self.tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False

    def get_names(self) -> set[str]: 
        """Get register of names

        Returns:
            set[str]: All names of collection elements.
        """
        return self._names

    def get_item_model(self, name: str) -> TauFit|None:
        """Get TauFit of given name

        Args:
            name (str): Name of TauFit to retrieve.

        Returns:
            Fit | None: TauFit with given name or None if it is not part of collection.
        """
        for f in self._tau_fits:
            if f.name == name:
                return f
        else:
            return None

    def get_jsonable(self) -> list:
        """Marshal collection to python list of dictionaries.

        Returns:
            list[dict]: All TauFits in collection marshaled into dictionaries.
        """
        jsonable: list = [f.get_jsonable() for f in self._tau_fits]
        return jsonable

    def from_json(self, fits: list[dict]):
        """Append new TauFits created from result of get_jsonable()."""
        for f in fits:
            new_model: TauFit = TauFit(f["name"], self._compound, cast(Collection, self))
            new_model.update_from_json(f)
            self.append_tau_fit(new_model)