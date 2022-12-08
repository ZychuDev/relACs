from .Parameter import Parameter, PARAMETER_NAME
from protocols import SettingsSource

FrequencyParameters = tuple[Parameter, Parameter, Parameter, Parameter, Parameter]
class Relaxation():
    def __init__(self, compound: SettingsSource):
        
        self.parameters: FrequencyParameters  = (
            Parameter("alpha", compound.get_min("alpha"), compound.get_max("alpha")),
            Parameter("beta", compound.get_min("beta"), compound.get_max("beta")),
            Parameter("tau", compound.get_min("tau"), compound.get_max("tau"), is_log=True),
            Parameter("chi_t", compound.get_min("chi_t"), compound.get_max("chi_t")),
            Parameter("chi_s", compound.get_min("chi_s"), compound.get_max("chi_s")),
        )
        self.saved_parameters: FrequencyParameters = (
            Parameter("alpha", compound.get_min("alpha"), compound.get_max("alpha")),
            Parameter("beta", compound.get_min("beta"), compound.get_max("beta")),
            Parameter("tau", compound.get_min("tau"), compound.get_max("tau"), is_log=True),
            Parameter("chi_t", compound.get_min("chi_t"), compound.get_max("chi_t")),
            Parameter("chi_s", compound.get_min("chi_s"), compound.get_max("chi_s")),
        )

        self.residual_error = 0.0
        self.saved_residual_error = 0.0

    def get_parameters_values(self) -> tuple[float, float, float, float, float]:
        return tuple(p.value for p in self.parameters) # type: ignore

    def get_parameters_min_bounds(self):
        return [p.min for p in self.parameters]

    def get_parameters_max_bounds(self):
        return [p.max for p in self.parameters]

    def get_saved_parameters_values(self) -> tuple[float, float, float, float, float]:
        return tuple(p.value for p in self.saved_parameters) # type: ignore

    def get_jsonable(self):
        pass

    def from_json(self, json):
        pass