from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QTreeView
from protocols import Collection, Displayer 
from models import PARAMETER_NAME, TAU_PARAMETER_NAME
from readers import SettingsReader

class Compound(QObject):
    """Represent examined Compound

    Args:
        name (str): Name of Compound.
        molar_mass (float): Molar mass of compound in g/mol.
        collection (Collection | None): The collection to which it belongs. 
        tree (QTreeView): Control tree reference. Necessary for expanding tree after creating/removing tree elements.
        displayer (Displayer): Object responsible for visualization of Measurements, Fits and TauFits 
    """
    name_changed: pyqtSignal= pyqtSignal(str)
    def __init__(self, name: str, molar_mass: float, collection: Collection["Compound"]|None, tree:QTreeView, displayer: Displayer):
        super().__init__()

        if molar_mass < 0:
            raise ValueError(f"Compund molar mase({molar_mass}) must be greater than 0. ")
            
        self._name: str = name #: Name of Compound
        self._molar_mass: float = molar_mass

        self._collection: Collection|None = collection
        self._tree: QTreeView = tree
        self._displayer: Displayer = displayer

        settings: SettingsReader = SettingsReader()
        self._ranges: dict[str, tuple[float, float]] = settings.get_ranges()


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Compund name must be at least one character long")
        if self._collection is not None:
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
        """Marshal object to python dictionary

        Returns:
            dict: Dictionary ready to save as .json
        """
        jsonable: dict = {"name": self._name, "molar_mass":self._molar_mass}
        return jsonable

# TO DO
    def get_min(self, param_name: str) -> float:
        """Get lower boundry for given parameter name.

        Args:
            param_name (str): Name of the parameter.

        Returns:
            float: Lower boundry on parameter value.
        """

        return self._ranges[param_name][0]

# TO DO
    def get_max(self, param_name: str) -> float:
        """Get upper boundry for given parameter name.

        Args:
            param_name (str): Parameter name.

        Returns:
            float: Upper boundry on parameter value.
        """

        return self._ranges[param_name][1]
