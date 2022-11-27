from PyQt6.QtCore import QObject, pyqtSignal

from protocols import Collection, SettingsSource # type: ignore
from readers import SettingsReader

from pandas import DataFrame, Series # type: ignore
from math import log10, floor
from numpy import zeros

class Measurement(QObject):
    name_changed = pyqtSignal(str)
    columns_headers = ["Temperature","MagneticField","ChiPrime","ChiBis","Frequency"]

    def from_data_frame(df: DataFrame, sufix:str, compound:SettingsSource, collection: Collection):
        settings: SettingsReader = SettingsReader()
        field_epsilon: float
        temp_epsilon: float
        field_epsilon, temp_epsilon = settings.get_epsilons()
        
        accuracy_temp: float = log10(temp_epsilon)
        if(temp_epsilon >= 1):
            accuracy_temp = 0
        else:
            accuracy_temp = abs(floor(accuracy_temp) + 1)

        accuracy_field: float = log10(field_epsilon)
        if(temp_epsilon >= 1):
            accuracy_field = 0
        else:
            accuracy_field = abs(floor(accuracy_field) + 1)
        
        temp = round((df["Temperature"].max() + df["Temperature"].min())/2, accuracy_temp)
        field = round((df["MagneticField"].max() + df["MagneticField"].min())/2, accuracy_field)
        
        name = f"T: {temp}K H: {field}Oe {sufix}"
        length: int = len(df["Frequency"])
        df["Selected"] = Series(zeros(length), index=df.index)
        return Measurement(df, name, temp, field, compound, collection)


    def __init__(self, df: DataFrame, name: str, temp:float, field:float, compound: SettingsSource, collection: Collection):
        super().__init__()
        self._name: str = name
        self._df: DataFrame = df
        self._tmp: float = temp
        self._field: float = field

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


