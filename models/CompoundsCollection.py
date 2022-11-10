from .Compound import Compound
from PyQt6.QtCore import QObject, pyqtSignal
class CompoundsCollection(QObject):
    name_changed = pyqtSignal(str)

    def __init__(self, name:str):
        super().__init__()
        self._name = name

        self._compounds: list[Compound] = []
        self._names: set[str] = set()

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name:str):
        self._name = new_name
        self.name_changed.emit(new_name)
        
    def append_compound(self, compound: Compound):
        if compound.name in self._names:
            raise ValueError(f"Compund with name {compound.name} already exist in this collection")
        self._names.add(compound.name)
        self._compounds.append(compound)

    def delete_compund(self, compound_name:str):
        if compound_name in self._names:
            self._names.remove(compound_name)
            self._compounds = [compound for compound in self._compounds if compound.name != compound_name]
    



    