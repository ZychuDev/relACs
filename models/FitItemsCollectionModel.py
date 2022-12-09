from .Compound import Compound
from .Fit import Fit
from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush

class FitItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    fit_added = pyqtSignal(Fit)
    fit_removed = pyqtSignal(QModelIndex)
    displayed_item_changed = pyqtSignal(Fit)
    
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
        if fit.name in self._names:
            print(f"Fit with name {fit.name} already exists.\n Loading skipped")
            return

        self._fits.append(fit)
        self._names.add(fit.name)
        fit._collection = self
        if not silent:
            self.fit_added.emit(fit)
        if display:
            self.change_displayed_item(fit.name)

    def remove(self, fit_name: str, index: QModelIndex):
        if fit_name in self._names:
            self._names.remove(fit_name)
            self._measurements = [fit for fit in self._fits if fit.name in self._names]
            self.fit_removed.emit(index)

    def check_name(self, name: str) -> bool:
        return name in self._names

    def update_names(self, old_name: str, new_name: str):
        self._names.remove(old_name)
        self._names.add(new_name)

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        selected: list[QModelIndex] = self.tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False

    def change_displayed_item(self, name: str):
        new_item: Fit = next(fit for fit in self._fits if fit.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)

    def get_next(self, name: str) -> str:
        for i, f in enumerate(self._fits):
            if f.name == name:
                break

        if i == len(self._fits)-1:
            return self._fits[0].name
        else:
            return self._fits[i+1].name

    def get_previous(self, name: str) -> str:
        for i, f in enumerate(self._fits):
            if f.name == name:
                break

        if i == 0:
            return self._fits[-1].name
        else:
            return self._fits[i-1].name

    def get_item_model(self, name: str):
        for f in self._fits:
            if f.name == name:
                return f
        else:
            return None

    def get_names(self) -> list[str]: 
        return self._names
    