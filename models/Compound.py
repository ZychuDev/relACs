from PyQt6.QtCore import QObject, pyqtSignal

class Compound(QObject):
    name_changed = pyqtSignal(str)
    def __init__(self, name: str, molar_mas: float):
        super().__init__()
        self._name: str = name
        self._molar_mass:float = molar_mas

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Compund name must be at least one character long")
        self._name = val
        self.name_changed.emit(val)

    @property
    def molar_mass(self):
        return self._molar_mase

    @molar_mass.setter
    def molar_mass(self, val:float):
        if val <= 0:
            raise ValueError("Molar mass must be greater than 0")

        self._molar_mase = val
