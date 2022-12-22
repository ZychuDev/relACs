from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QTreeView
from protocols import Collection, Displayer 

class Compound(QObject):
    name_changed = pyqtSignal(str)
    def __init__(self, name: str, molar_mass: float, collection: Collection, tree:QTreeView, displayer: Displayer):
        super().__init__()

        if molar_mass < 0:
            raise ValueError(f"Compund molar mase({molar_mass}) must be greater than 0. ")
            
        self._name: str = name
        self._molar_mass: float = molar_mass

        self._collection: Collection = collection
        self._tree: QTreeView = tree
        self._displayer: Displayer = displayer

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


    def get_jsonable(self) -> dict:
        jsonable: dict = {"name": self._name, "molar_mass":self._molar_mass}
        return jsonable

# TO DO
    def get_min(self, param_name: str):
        map = {"alpha" : 0.0, 
            "beta" : 0.0, 
            "log10_tau" : -10.0, 
            "chi_t" : 0.0, 
            "chi_s" : 0.0,
            "a_dir" : 0.000_000_000_000_001,
            "n_dir" : 0.0,
            "b1" : 0.000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_001,
            "b2" : 0.000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_001,
            "b3" : 0.000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_000_001,
            "c_raman" : 0.0,
            "n_raman" : 0.0,
            "tau_0" : 0.1,
            "delta_e" : 0.0
        }
        return map[param_name]

# TO DO
    def get_max(self, param_name: str):
        map = {"alpha" : 1.0, 
            "beta" : 1.0, 
            "log10_tau" : 0.0, 
            "chi_t" : 30.0, 
            "chi_s" : 30.0,
            "a_dir" : 100,
            "n_dir" : 8.0,
            "b1" : 11_000_000_000_000.0,
            "b2" : 10.0,
            "b3" : 10.0,
            "c_raman" : 1.0,
            "n_raman" : 15.0,
            "tau_0" : 100_000_000_000_000_000_000_000_000.0,
            "delta_e" : 3000.0
        }
        return map[param_name]
