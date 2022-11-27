from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex
from PyQt6.QtGui import QColor, QBrush

from .Measurement import Measurement
from .Compound import Compound


class MeasurementItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    measurement_added = pyqtSignal(Compound)
    measurement_removed = pyqtSignal(QModelIndex)

    def __init__(self, name:str, compound:Compound):
        super().__init__()
        self._name: str = name
        self._compound: Compound = compound

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._measurements: list[Measurement] = []
        self._names: set[str] = set()

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Measurement name must be at least one character long")

        self._name = val
        self.name_changed.emit(val)

    @property
    def model(self):
        return self._model
        
    def append_measurement(self, measurement: Measurement):
        self._measurements.append(measurement)
        self._names.add(measurement.name)
        self.measurement_added.emit(measurement)

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




    