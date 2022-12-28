from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush

from .Measurement import Measurement
from .Compound import Compound

from pandas import read_json # type: ignore

from protocols import Collection
from typing import cast

class MeasurementItemsCollectionModel(QObject):
    """_summary_

        Args:
            name (str): _description_
            compound (Compound): _description_

        Attributes:
            name_changed: Emitted when collection name is changed. Contains new name.
            measurement_added: Emitted when new Measurement is added to collection. Contains new Measurement.
            measurement_removed: Emitted when Measurement is removed from collection. Contains removed Measurement's Index in controll tree.
            displayed_item_changed: Emitted when displayed Measurement is replaced.
    """

    name_changed: pyqtSignal = pyqtSignal(str)
    measurement_added: pyqtSignal = pyqtSignal(Compound)
    measurement_removed: pyqtSignal = pyqtSignal(QModelIndex)
    displayed_item_changed: pyqtSignal = pyqtSignal(Measurement)

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
        """Replace currently displayed Measurement.

        Args:
            name (str): Name of the Measurement to display.
        """

        new_item: Measurement = next( measurement for measurement in self._measurements if measurement.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)

    def append_measurement(self, measurement: Measurement, silent: bool=False, display: bool=False):
        """Apped Measurement to collection

        Args:
            measurement (Measurement): Measurement to add to collection 
            silent (bool, optional): Determines whether fit_added signal will be emitted. Defaults to False.
            display (bool, optional): Determines whether display newly added Fit. Defaults to False.
        """

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
        """Remove Measurement with given name from collection.

        Args:
            measurement_name (str): Name of Measurement to remove.
            index (QModelIndex): Removed Measurement's index in controll tree.
        """

        if measurement_name in self._names:
            self._names.remove(measurement_name)
            self._measurements = [measurement for measurement in self._measurements if measurement.name in self._names]
            self.measurement_removed.emit(index)

    def check_name(self, name: str) -> bool:
        """Check if Measurement with given name is already in collection.

        Args:
            name (str): Measurement  name.

        Returns:
            bool: If name is already taken.
        """

        return name in self._names

    def update_names(self, old_name: str, new_name: str):
        """Updates name register in collection.

        Args:
            old_name (str): Old Measurement name.
            new_name (str): New Measurement name.
        """
        self._names.remove(old_name)
        self._names.add(new_name)

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        """Checks Measurement select state.

        Args:
            index (QModelIndex): Measurement Index in cotroll tree.

        Returns:
            bool: Check state.
        """

        selected: list[QModelIndex] = self.tree.selectedIndexes()
        for selected_index in selected:
            if selected_index == index:
                return True
        return False

    def get_jsonable(self) -> list:
        """Marshal collection to python list of dictionaries.

        Returns:
            list[dict]: All Measurements in collection marshaled into dictionaries.
        """

        jsonable: list = [measurement.get_jsonable() for measurement in self._measurements]
        return jsonable

    def from_json(self, measurements: list[dict]):
        """Append new Measurements created from result of get_jsonable()"""
        for m in measurements:
            new_model = Measurement(read_json(m["df"]), m["name"], m["tmp"], m["field"], self._compound, cast(Collection, self))
            self.append_measurement(new_model)




    