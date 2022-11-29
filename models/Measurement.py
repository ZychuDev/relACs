from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from protocols import Collection, SettingsSource # type: ignore
from readers import SettingsReader

from pandas import DataFrame, Series # type: ignore
from math import log10, floor
from numpy import zeros

class Measurement(QObject):
    name_changed = pyqtSignal(str)
    df_changed= pyqtSignal()
    
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
        df["Hidden"] = Series(zeros(length), index=df.index)
        return Measurement(df, name, temp, field, compound, collection)


    def __init__(self, df: DataFrame, name: str, temp:float, field:float, compound: SettingsSource, collection: Collection):
        super().__init__()
        self._name: str = name
        self._df: DataFrame = df
        self._tmp: float = temp
        self._field: float = field

        self._compound: SettingsSource = compound
        self._collection: Collection = collection

    # @property
    # def df(self):
    #     return self._df

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

    def hide_point(self, x: float, x_str: str):
        actual: bool = bool(self._df.loc[self._df[x_str] == x]['Hidden'].values[0])
        self._df.loc[self._df[x_str] == x, "Hidden"] = not actual
        self.df_changed.emit()
        # self.dataChanged.emit() #type: ignore

    def delete_point(self, x: float, x_str: str):
        if self._df.shape[0] == 2:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Measurement must consist of at least 2 data points")
            msg.setWindowTitle("Data point removal error")
            msg.exec()
            return

        self._df.drop(self._df.loc[self._df[x_str] == x].index, inplace=True)
        self.df_changed.emit()
        # self.dataChanged.emit() #type: ignore


