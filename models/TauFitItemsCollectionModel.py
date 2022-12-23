from .Compound import Compound
from .TauFit import TauFit

from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush

from protocols import Collection
from typing import cast

class TauFitItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    fit_added = pyqtSignal(TauFit)
    fit_removed = pyqtSignal(QModelIndex)
    displayed_item_changed = pyqtSignal(TauFit)

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
        
    def add_tau_fit(self, compound: Compound):
        pass

    def delete_tau_fit(self, compound_name:str):
        pass

    def remove(self, tau_fit_name: str, index: QModelIndex):
        if tau_fit_name in self._names:
            self._names.remove(tau_fit_name)
            self._tau_fits = [fit for fit in self._tau_fits if fit.name in self._names]
            self.fit_removed.emit(index)

    def update_names(self, old_name: str, new_name: str):
        self._names.remove(old_name)
        self._names.add(new_name)

    def check_name(self, name: str) -> bool:
        return name in self._names

    def change_displayed_item(self, name: str):
        new_item: TauFit = next(fit for fit in self._tau_fits if fit.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)

    def append_tau_fit(self, fit: TauFit, silent: bool=False, display: bool=False):
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
        selected: list[QModelIndex] = self.tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False

    def get_names(self) -> set[str]: 
        return self._names

    def get_item_model(self, name: str):
        for f in self._tau_fits:
            if f.name == name:
                return f
        else:
            return None