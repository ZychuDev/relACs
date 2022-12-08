from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from .Relaxation import Relaxation
from models import Measurement
from .Parameter import Parameter

from protocols import Collection, SettingsSource

from pandas import DataFrame # type: ignore


class Fit(QObject):
    name_changed = pyqtSignal(str)
    df_changed= pyqtSignal()
    df_point_deleted = pyqtSignal()
    parameter_changed = pyqtSignal()
    fit_changed = pyqtSignal()

    @staticmethod
    def from_measurement(measurement: Measurement, compound:SettingsSource, nr_of_relaxations: int = 1):
        fit_name: str = measurement._name + "_Fit_Frequency"
        fit: Fit =  Fit(fit_name, measurement._df.copy(), measurement._tmp, measurement._field, compound, None)

        fit.relaxations = []
        i: int
        for i in range(nr_of_relaxations):
            fit.relaxations.append(Relaxation(compound))

        return fit
    def __init__(self, name: str, df: DataFrame, temp: float, field: float, compound:SettingsSource, collection: Collection):
        super().__init__()
        self._name: str = name
        self._df: DataFrame = df

        self._tmp: float = temp
        self._field: float = field

        self.relaxations: list[Relaxation]

        self._compound: SettingsSource = compound
        self._collection: Collection = collection

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
        self.df_point_deleted.emit()