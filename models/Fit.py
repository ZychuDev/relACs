from PyQt6.QtCore import QObject, pyqtSignal
from models import Measurement

from protocols import Collection, SettingsSource



class Fit(QObject):
    name_changed = pyqtSignal(str)
    parameter_changed = pyqtSignal()
    fit_changed = pyqtSignal()

    @staticmethod
    def from_measurement(measurement: Measurement, compound:SettingsSource):
        fit_name: str = measurement._name + "_Fit_Frequency"
        return Fit(fit_name, compound, None)

    def __init__(self, name: str, compound:SettingsSource, collection: Collection):
        super().__init__()
        self._name: str = name

        self._compound: SettingsSource = compound
        self._collection: Collection = collection

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Compund name must be at least one character long")
        self._collection.update_names(self._name, val)
        self._name = val
        self.name_changed.emit(val)

    @property
    def molar_mass(self):
        return self._molar_mass

    @molar_mass.setter
    def molar_mass(self, val:float):
        if val <= 0:
            raise ValueError("Molar mass must be greater than 0")

        self._molar_mass = val