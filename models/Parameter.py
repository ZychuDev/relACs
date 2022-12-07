from PyQt6.QtCore import pyqtSignal, QObject

from .Literals import PARAMETER_NAME

class Parameter(QObject):
    value_changed = pyqtSignal(float)
    error_changed = pyqtSignal(float)

    name_to_symbol:dict[PARAMETER_NAME, str] = {
        "alpha": "\u03B1",
        "beta": "\u03B2",
        "tau": "\u03C4",
        "chi_t": "\u03C7\u209C",
        "chi_s": "\u03C7\u209B"
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

    def get_range(self) -> tuple[float, float]:
        return (self.min, self.max)

    def set_value(self, v: float, silent: bool=False):
        if v < self.min or v > self.max:
            raise ValueError(f"Value {v} is out of bonds ({self.min} {self.max}) for parameter {self.name}")
        self.value = v
        if not silent:
            self.value_changed.emit(v)

    def set_error(self, v: float):
        self.error = v
        self.error_changed.emit(v)

    def set_blocked(self, block: bool):
        self.is_blocked = block
