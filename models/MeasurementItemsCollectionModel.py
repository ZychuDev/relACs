from .Compound import Compound
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

class MeasurementItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)

    def __init__(self, name:str):
        super().__init__()
        self._name: str = name

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._compounds: list[Compound] = []
        self._names: set[str] = set()


    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name:str):
        self._name = new_name
        self.name_changed.emit(new_name)
        
    def append_measurement(self, compound: Compound):
        pass

    def delete_measurement(self, compound_name:str):
        pass



    