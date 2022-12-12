from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush

from .Measurement import Measurement
from .Compound import Compound

from pandas import read_json # type: ignore

from protocols import Collection
from typing import cast

class MeasurementItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    measurement_added = pyqtSignal(Compound)
    measurement_removed = pyqtSignal(QModelIndex)
    displayed_item_changed = pyqtSignal(Measurement)

    def __init__(self, name: str, compound: Compound):
        super().__init__()
        self._name: str = name
        self._compound: Compound = compound

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._measurements: list[Measurement] = []
        self._names: set[str] = set()

        self._displayed_item: Measurement

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

    def change_displayed_item(self, name: str):
        new_item: Measurement = next( measurement for measurement in self._measurements if measurement.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)

    def append_measurement(self, measurement: Measurement, silent: bool=False, display: bool=False):
        if measurement.name in self._names:
            print(f"Measurements with name {measurement.name} already exists.\n Loading skipped")
            return

        self._measurements.append(measurement)
        self._names.add(measurement.name)
        if not silent:
            self.measurement_added.emit(measurement)
        if display:
            self.change_displayed_item(measurement.name)

    def remove(self, measurement_name: str, index: QModelIndex):
        if measurement_name in self._names:
            self._names.remove(measurement_name)
            self._measurements = [measurement for measurement in self._measurements if measurement.name in self._names]
            self.measurement_removed.emit(index)

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

    def get_jsonable(self) -> list:
        jsonable: list = [measurement.get_jsonable() for measurement in self._measurements]
        return jsonable

    def from_json(self, measurements: list[dict]):
        for m in measurements:
            new_model = Measurement(read_json(m["df"]), m["name"], m["tmp"], m["field"], self._compound, cast(Collection, self))
            self.append_measurement(new_model)




    