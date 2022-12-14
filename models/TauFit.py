from PyQt6.QtCore import QObject, pyqtSignal
from .Parameter import Parameter, TAU_PARAMETER_NAME
from .Point import Point
from .Fit import Fit

from protocols import Collection, SettingsSource

from typing import get_args

from numpy import power, exp

TauParameters = tuple[Parameter, ...]

class TauFit(QObject):
    name_changed = pyqtSignal(str)
    parameter_changed = pyqtSignal()
    fit_changed = pyqtSignal()
    points_changed = pyqtSignal()

    @staticmethod
    def direct(temp:float, field:float, a_dir:float, n_dir:float):
        return a_dir * temp * power(field, n_dir)

    @staticmethod
    def qtm(field:float, b1:float, b2:float, b3:float):
        return b1*(1+b3*field*field)/(1+b2*field*field)

    @staticmethod
    def Raman(temp:float, c_raman:float, n_raman:float):
        return c_raman* power(temp, n_raman)

    @staticmethod
    def Orbach(temp:float, tau_0:float, delta_e:float):
        return tau_0 * exp(-delta_e/temp)

    @staticmethod
    def model(temp:float, field:float, a_dir:float, n_dir:float, b1:float, b2:float,
     b3: float, c_raman:float, n_raman:float, tau_0:float, delta_e:float):
        return a_dir*temp*(field**n_dir) \
            + b1*(1+b3*field*field)/(1+b2*field*field) \
            + c_raman * power(temp, n_raman) \
            + tau_0 *exp(-delta_e/(temp))

    @staticmethod
    def from_fit(compound: SettingsSource, collection=None):
        t_fit: TauFit = TauFit("abc", compound, collection)

        return t_fit

    def __init__(self, name: str, compound: SettingsSource, collection: Collection|None):
        super().__init__()
        self._name: str = name
        self._residual_error: float = 0.0
        self._saved_residual_erro: float = 0.0
        self.parameters: TauParameters  = tuple( 
            Parameter(name, compound.get_min(name), compound.get_max(name)) for name in get_args(TAU_PARAMETER_NAME)
        )

        self.saved_parameters: TauParameters = tuple( 
            Parameter(name, compound.get_min(name), compound.get_max(name)) for name in get_args(TAU_PARAMETER_NAME)
        )

        self._points: list[Point] = []

        self._collection: Collection
        if collection is not None:
            self._collection = collection

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Tau fit name must be at least one character long")
        self._name = val
        self.name_changed.emit(val)

    def append_point(self, tau:float, temp:float, field:float, silent=False):
        point: Point = Point(tau, temp, field)
        self._points.append(point)
        if not silent:
            self.points_changed.emit()

    def get_hidden(self) -> tuple[list[float], list[float], list[float]]:
        r_tau: list[float] = []
        r_temp: list[float] = []
        r_field: list[float] = []
        for p in self._points:
            if not p.is_hidden:
                r_tau.append(p.tau)
                r_temp.append(p.temp)
                r_field.append(p.field)

        return (r_tau, r_temp, r_field)


    def get_visible(self) -> tuple[list[float], list[float], list[float]]:
        r_tau: list[float] = []
        r_temp: list[float] = []
        r_field: list[float] = []
        for p in self._points:
            if not p.is_hidden:
                r_tau.append(p.tau)
                r_temp.append(p.temp)
                r_field.append(p.field)

        return (r_tau, r_temp, r_field)

    