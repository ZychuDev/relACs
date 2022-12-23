from PyQt6.QtCore import QObject, pyqtSignal
from .Parameter import Parameter, TAU_PARAMETER_NAME
from .Point import Point
from .Fit import Fit

from protocols import Collection, SettingsSource

from typing import get_args, Literal
from functools import partial

from scipy.optimize import least_squares # type: ignore
from scipy.linalg import svd #type: ignore

from numpy import power, exp, log, finfo, sqrt, diag
from numpy import max as np_max

from math import nextafter

from pandas import Series #type: ignore

TauParameters = tuple[Parameter, ...]

class TauFit(QObject):
    name_changed = pyqtSignal(str)
    parameter_changed = pyqtSignal()
    all_parameters_changed = pyqtSignal()
    fit_changed = pyqtSignal()
    points_changed = pyqtSignal()
    varying_changed = pyqtSignal(str)
    constant_changed = pyqtSignal(float)
    parameters_saved = pyqtSignal()

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
    def from_fit(name:str, compound: SettingsSource, collection=None):
        t_fit: TauFit = TauFit(name, compound, collection)

        return t_fit

    def __init__(self, name: str, compound: SettingsSource, collection: Collection|None):
        super().__init__()
        self._name: str = name
        self.residual_error: float = 0.0
        self.saved_residual_erro: float = 0.0
        logaritmic = ["a_dir", "b1", "b2", "b3", "tau_0"]
        self.parameters: TauParameters  = tuple( 
            Parameter(name, compound.get_min(name), compound.get_max(name), is_log = name in logaritmic) for name in get_args(TAU_PARAMETER_NAME)
        )

        self.saved_parameters: TauParameters = tuple( 
            Parameter(name, compound.get_min(name), compound.get_max(name), is_log = name in logaritmic) for name in get_args(TAU_PARAMETER_NAME)
        )

        self._points: list[Point] = []

        self.varying: Literal["Field", "Temperature"] = "Field"
        self.constant: float = 0

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
            if p.is_hidden:
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

    def get_all(self) -> tuple[list[float], list[float], list[float]]:
        tmp: list = list(zip(*[(p.tau, p.temp, p.field) for p in self._points]))
        return (tmp[0], tmp[1], tmp[2])

    def get_visible_s(self) -> tuple[list[float], list[float], list[float]]:
        r_tau: list[float] = []
        r_temp: list[float] = []
        r_field: list[float] = []
        for p in self._points:
            if not p.is_hidden:
                if self.get_constant_from_point(p) == self.constant:
                    r_tau.append(p.tau)
                    r_temp.append(p.temp)
                    r_field.append(p.field)
        return (r_tau, r_temp, r_field)

    def get_hidden_s(self) -> tuple[list[float], list[float], list[float]]:
        r_tau: list[float] = []
        r_temp: list[float] = []
        r_field: list[float] = []
        for p in self._points:
            if p.is_hidden:
                if self.get_constant_from_point(p) == self.constant:
                    r_tau.append(p.tau)
                    r_temp.append(p.temp)
                    r_field.append(p.field)
        return (r_tau, r_temp, r_field)

    def get_all_s(self) -> tuple[list[float], list[float], list[float]]:
        tmp: list = list(zip(*[(p.tau, p.temp, p.field) for p in self._points if self.get_constant_from_point(p) == self.constant]))
        try:
            return (tmp[0], tmp[1], tmp[2])
        except Exception:
            return ([], [], [])

    def get_constant_from_point(self, p:Point):
        if self.varying == "Field":
            return p.temp
        else:
            return p.field

    def set_varying(self, txt: Literal["Field","Temperature"]):
        self.varying = txt
        self.varying_changed.emit(self.varying)

    def set_constant(self, value: float):
        self.constant = value
        self.constant_changed.emit(value)

    def hide_point(self, v: float, z: float):
        for p in self._points:
            if self.varying == "Field":
                if p.field == v and p.temp == self.constant and log(p.tau) == z:
                    p.is_hidden = not p.is_hidden
                    break
            else:
                if p.temp == 1/v and p.field == self.constant and log(p.tau) == z:
                    p.is_hidden = not p.is_hidden
                    break
        self.points_changed.emit()

    def delete_point(self, v: float, z: float):
        old_points: list[Point] = self._points
        if self.varying == "Field":
            self._points = [p for p in self._points if (p.field, p.temp, log(p.tau)) != (v, self.constant, z)]
        else:
            self._points = [p for p in self._points if (p.temp,  p.field, log(p.tau)) != (1/v, self.constant, z)]

        if len(self._points) < 2:
            self._points = old_points

        self.points_changed.emit()

    def get_parameters_values(self) -> tuple[float, float, float, float, float]:
        return tuple(p.value for p in self.parameters) # type: ignore

    def get_saved_parameters_values(self) -> tuple[float, float, float, float, float]:
        return tuple(p.value for p in self.saved_parameters) # type: ignore

    def get_parameters_min_bounds(self):
        return [p.min for p in self.parameters]

    def get_parameters_max_bounds(self):
        return [p.max for p in self.parameters]

    def make_auto_fit(self, slice_flag=False):
        params = self.get_parameters_values()
        min = self.get_parameters_min_bounds()
        max = self.get_parameters_max_bounds()

        p:Parameter
        for i, p in enumerate(self.parameters):
            if p.is_blocked:
                min[i] = nextafter(p.value, min[i])
                max[i] = nextafter(p.value, max[i])

            if p.is_blocked_on_0:
                params = list(params)
                min[i] = nextafter(nextafter(0.0, 1), 0)
                max[i] = nextafter(nextafter(0.0, 1), 1)
                params[i] = nextafter(0.0, 1)

            if p.value < min[i] and not p.is_blocked_on_0:
                tmp: float = nextafter(min[i], max[i])
                p.set_value(tmp)
                params = list(params)
                params[i] = tmp

        bounds: tuple[list[float], list[float]] = (min, max)
        cost_f = partial(self.cost_function, slice=slice_flag)

        res = least_squares(cost_f, params, bounds=bounds)

        for i, p in enumerate(self.parameters):
            p.set_value(res.x[i])

        _, s, Vh = svd(res.jac, full_matrices=False)
        tol = finfo(float).eps*s[0]*np_max(res.jac.shape)
        w = s > tol
        cov = (Vh[w].T/s[w]**2) @ Vh[w]

        chi2dof = sum(res.fun**2)/(res.fun.size - res.x.size)
        cov *= chi2dof

        perr = sqrt(diag(cov))
        self.set_all_errors(res.cost, perr)

    def cost_function(self, p, slice=False):
        if slice:
            tau, temp, field = self.get_all_s()
        else:
            tau, temp, field = self.get_all()
        temp = Series(temp)
        field = Series(field)
        tau = Series(tau)
        return power(log(TauFit.model(temp, field, *p)) - log(1/tau), 2)

    def set_all_errors(self, residual_error: float, params_error: list[float]):
        self.residual_error = residual_error
        p: Parameter
        for i, p in enumerate(self.parameters):
            p.set_error(params_error[i], silent=True)
        self.all_parameters_changed.emit()

    def save(self):
        for i, p in enumerate(self.parameters):
            s = self.saved_parameters[i]
            s.set_value(p.value)
            s.set_blocked(p.is_blocked)
            s.set_blocked_0(p.is_blocked_on_0)
            s.set_error(p.error)
        self.parameters_saved.emit()

    def reset(self):
        for i, p in enumerate(self.parameters):
            s = self.saved_parameters[i]
            p.set_value(s.value)
            p.set_blocked(s.is_blocked)
            p.set_blocked_0(s.is_blocked_on_0)
            p.set_error(s.error)

        self.all_parameters_changed.emit()

    def copy(self, other):
        for i, p in enumerate(self.parameters):
            o = other.saved_parameters[i]
            p.set_value(o.value)
            p.set_blocked(o.is_blocked)
            p.set_blocked_0(o.is_blocked_on_0)
            p.set_error(o.error)

        self.all_parameters_changed.emit()