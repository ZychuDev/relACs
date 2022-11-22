from .Compound import Compound
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

class CompoundItemsCollectionModel(QObject):
    name_changed = pyqtSignal(str)
    compound_added = pyqtSignal(Compound)

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
        
    def append_new_compound(self, name: str, molar_mass: float):
        if name in self._names:
            raise ValueError(f"Compund with name {name} already exist in this collection")
        
        new: Compound = Compound(name, molar_mass)
        self._compounds.append(new)
        self._names.add(name)
        self.compound_added.emit(new)
        

    def delete_compund(self, compound_name:str):
        if compound_name in self._names:
            self._names.remove(compound_name)
            self._compounds = [compound for compound in self._compounds if compound.name != compound_name]

    def check_name(self, name: str) -> bool:
        return name in self._names
    



    