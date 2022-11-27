from PyQt6.QtCore import QObject, pyqtSignal

from protocols import Collection, SettingsSource

class Measurement(QObject):
    name_changed = pyqtSignal(str)
    def __init__(self, name: str, compound: SettingsSource, collection: Collection):
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
        self._name = val
        self.name_changed.emit(val)

