from .Parameter import Parameter, PARAMETER_NAME
from protocols import SettingsSource 
from PyQt6.QtCore import pyqtSignal, QObject

from numpy import power

FrequencyParameters = tuple[Parameter, Parameter, Parameter, Parameter, Parameter]
class Relaxation(QObject):
    parameters_saved = pyqtSignal()
    all_parameters_changed = pyqtSignal()
    all_error_changed = pyqtSignal(float)

    def __init__(self, compound: SettingsSource):
        super().__init__()
        self.parameters: FrequencyParameters  = (
            Parameter("alpha", compound.get_min("alpha"), compound.get_max("alpha")),
            Parameter("beta", compound.get_min("beta"), compound.get_max("beta")),
            Parameter("log10_tau", compound.get_min("log10_tau"), compound.get_max("log10_tau")),
            Parameter("chi_t", compound.get_min("chi_t"), compound.get_max("chi_t")),
            Parameter("chi_s", compound.get_min("chi_s"), compound.get_max("chi_s")),
        )
        self.saved_parameters: FrequencyParameters = (
            Parameter("alpha", compound.get_min("alpha"), compound.get_max("alpha")),
            Parameter("beta", compound.get_min("beta"), compound.get_max("beta")),
            Parameter("log10_tau", compound.get_min("log10_tau"), compound.get_max("log10_tau")),
            Parameter("chi_t", compound.get_min("chi_t"), compound.get_max("chi_t")),
            Parameter("chi_s", compound.get_min("chi_s"), compound.get_max("chi_s")),
        )

        self.residual_error = 0.0
        self.saved_residual_error = 0.0
        self.was_saved: bool = False

    def save(self):
        for i, p in enumerate(self.parameters):
            s = self.saved_parameters[i]
            s.set_value(p.value)
            s.set_blocked(p.is_blocked)
            s.set_error(p.error)
        self.was_saved = True
        self.parameters_saved.emit()

    def reset(self):
        for i, p in enumerate(self.parameters):
            s = self.saved_parameters[i]
            p.set_value(s.value)
            p.set_blocked(s.is_blocked)
            p.set_error(s.error)

        self.all_parameters_changed.emit()

    def copy(self, other):
        for i, p in enumerate(self.parameters):
            o = other.saved_parameters[i]
            p.set_value(o.value)
            p.set_blocked(o.is_blocked)
            p.set_error(o.error)

        self.all_parameters_changed.emit()

    def set_all_errors(self, residual_error: float, params_error: list[float]):
        self.residual_error = residual_error
        for i, er in enumerate(params_error):
            self.parameters[i].set_error(er, silent=True)
        self.all_parameters_changed.emit()

    def set_all_values(self, values: list[float]):
        for i, v in enumerate(values):
            self.parameters[i].set_value(v, silent=True)
        self.all_parameters_changed.emit()

    def get_parameters_values(self) -> tuple[float, float, float, float, float]:
        return tuple(p.value for p in self.parameters) # type: ignore

    def get_tau(self):
        return power(10, self.saved_parameters[2].value)

    def get_parameters_min_bounds(self):
        return [p.min for p in self.parameters]

    def get_parameters_max_bounds(self):
        return [p.max for p in self.parameters]

    def get_saved_parameters_values(self) -> tuple[float, float, float, float, float]:
        return tuple(p.value for p in self.saved_parameters) # type: ignore

    def get_jsonable(self) -> dict:
        p_list: list[dict] = []
        for p in self.parameters:
            p_list.append(p.get_jsonable())

        s_p_list: list[dict] = []
        for p in self.saved_parameters:
            s_p_list.append(p.get_jsonable())

        jsonable = {
         "residual_error": self.residual_error , 
         "saved_residual_error": self.saved_residual_error,
         "was_saved": self.was_saved,
         "parameters": p_list,
         "saved_parameters": s_p_list
        }
        return jsonable

    def from_json(self, json):
        pass