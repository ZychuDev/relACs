from .Compound import Compound
from .Fit import Fit
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

class FitItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    displayed_item_changed = pyqtSignal(Fit)
    
    def __init__(self, name:str):
        super().__init__()
        self._name: str = name

        self._font_size: int = 16 
        self._set_bold: bool = True
        self._color: QColor = QColor(255,122,0)

        self._fits: list[Fit] = []
        self._names: set[str] = set()


    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name:str):
        self._name = new_name
        self.name_changed.emit(new_name)
        
    def add_fit(self, compound: Compound):
        pass

    def delete_measurement(self, compound_name:str):
        pass

    def change_displayed_item(self, name: str):
        new_item: Fit = next( fit for fit in self._fits if fit.name == name)
        self._displayed_item = new_item
        self.displayed_item_changed.emit(new_item)



    