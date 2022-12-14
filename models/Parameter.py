from PyQt6.QtCore import pyqtSignal, QObject

from .Literals import PARAMETER_NAME, TAU_PARAMETER_NAME

class Parameter(QObject):
    value_changed = pyqtSignal(float)
    block_state_changed = pyqtSignal(bool)
    error_changed = pyqtSignal(float)

    name_to_symbol:dict[PARAMETER_NAME|TAU_PARAMETER_NAME, str] = {
        "alpha": "\u03B1",
        "beta": "\u03B2",
        "log10_tau": "log\u2081\u2080\u03C4",
        "chi_t": "\u03C7\u209C",
        "chi_s": "\u03C7\u209B",
        "a_dir" : "A dir",
        "n_dir" : "N dir",
        "b1" : "B\u2081",
        "b2" : "B\u2082",
        "b3" : "B\u2083",
        "c_raman" : "C raman",
        "n_raman" : "N raman",
        "tau_0" : "tau\u2080",
        "delta_e" : "\u0394E"
    }

    def __init__(self, name:PARAMETER_NAME, min:float, max:float,
     is_blocked: bool=False, is_log: bool = False):
        super().__init__()
        self.name: str = name
        self.symbol: str = Parameter.name_to_symbol[name]
        self.min: float = min
        self.max: float = max
        self.value: float = (max+min)/2
        self.error: float = 0.0
        self.is_blocked: bool = is_blocked
        self.is_log: bool = is_log

    def get_jsonable(self) -> dict:
        jsonable: dict = {
         "name": self.name, 
         "symbol": self.symbol,
         "min": self.min,
         "max": self.max,
         "value": self.value,
         "error": self.error,
         "is_blocked": self.is_blocked,
         "is_log": self.is_log,
        }
        return jsonable

    def update_from_json(self, j: dict):
        self.name = j["name"] 
        self.symbol = j["symbol"]
        self.min = j["min"]
        self.max = j["max"]
        self.value = j["value"]
        self.error = j["error"]
        self.is_blocked = j["is_blocked"]
        self.is_log = j["is_log"]

    def get_range(self) -> tuple[float, float]:
        return (self.min, self.max)

    def set_value(self, v: float, silent: bool=False):
        if v < self.min or v > self.max:
            raise ValueError(f"Value {v} is out of bonds ({self.min} {self.max}) for parameter {self.name}")
        self.value = v
        self.set_error(0)
        if not silent:
            self.value_changed.emit(v)

    def set_error(self, v: float, silent=False):
        self.error = v
        if not silent:
            self.error_changed.emit(v)

    def set_blocked(self, block: bool):
        self.is_blocked = block
        self.block_state_changed.emit(self.is_blocked)
