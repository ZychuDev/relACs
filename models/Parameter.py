from PyQt6.QtCore import pyqtSignal, QObject

from .Literals import PARAMETER_NAME, TAU_PARAMETER_NAME
from numpy import log10

class Parameter(QObject):
    """Represent single parameter of mathematical model used in fitting proces

        Args:
            name (PARAMETER_NAME|TAU_PARAMETER_NAME): Name of parameter. Used for deducting symbol(which is used in UI)_description_
            min (float): Minimal boundry of parameter value
            max (float): Maximal boundty of parameter value
            is_blocked (bool, optional): If set to true will redefine boundares for parameter in fitting proces to the smallest possible(around current parameter value) suported by 
                runtime enviroment. Defaults to False.
            is_log (bool, optional): Determines whether user input is interpreted as parameter value or it log10. Defaults to False.
            is_blocked_on_0 (bool, optional): If set to true parameter value will be set to the smallest value supported by 
                runtime environment when cost function in calculated. Defaults to False.

        Attributes:
            value_changed: Emitted when value changed. Contains new value.
            block_state_changed: Emitted when block state change. Contains new state.
            block_0_state_changed: Emitted when block on 0 state change. Contains new state.
            error_changed: Emitted when error value changed. Contains new error value.

            name_to_symbol: Map between parameters names and their symbols
    """
    range_changed: pyqtSignal = pyqtSignal(str)
    value_changed: pyqtSignal = pyqtSignal(float) 
    range_changed2: pyqtSignal = pyqtSignal(str)
    block_state_changed: pyqtSignal = pyqtSignal(bool)
    block_0_state_changed: pyqtSignal = pyqtSignal(bool)
    error_changed: pyqtSignal = pyqtSignal(float)
    reset_errors: pyqtSignal = pyqtSignal(bool)
    

    name_to_symbol:dict[PARAMETER_NAME|TAU_PARAMETER_NAME, str] = {
        "alpha": "\u03B1",
        "beta": "\u03B2",
        "log10_tau": "log\u2081\u2080\u03C4",
        "chi_dif": "\u03C7\u209C-\u03C7\u209B",
        "chi_s": "\u03C7\u209B",
        "a_dir" : "A<span style=\" vertical-align:sub;\">dir</span></p>",
        "n_dir" : "N<span style=\" vertical-align:sub;\">dir</span></p>",
        "b1" : "B\u2081",
        "b2" : "B\u2082",
        "b3" : "B\u2083",
        "c_raman_1" : "C<span style=\" vertical-align:sub;\">Raman<sub>1</sub></span></p>",
        "n_raman_1" : "N<span style=\" vertical-align:sub;\">Raman<sub>1</sub></span></p>",
        "c_raman_2" : "C<span style=\" vertical-align:sub;\">Raman<sub>2</sub></span></p>",
        "n_raman_2" : "N<span style=\" vertical-align:sub;\">Raman<sub>2</sub></span></p>",
        "m_2" : "m<sub>2</sub></p>",
        "tau_0" : "&tau;<span style=\" vertical-align:sub;\">0</span><span style=\" vertical-align:super;\">-1</span></p>",
        "delta_e" : "\u0394E",
        "v": "v<span style=\" vertical-align:sub;\">ph</span></p>",
        "d" : "d<span style=\" vertical-align:sub;\">ph</span></p>",
    }

    def __init__(self, name:PARAMETER_NAME|TAU_PARAMETER_NAME, min:float, max:float,
     is_blocked: bool=False, is_log: bool = False, is_blocked_on_0: bool = False):
        super().__init__()
        self.name: str = name
        self.symbol: str = Parameter.name_to_symbol[name]
        self.min: float = min 
        self.max: float = max 
        self.value: float = (max+min)/2 
        self.error: float = 0.0
        self.is_blocked: bool = is_blocked
        self.is_blocked_on_0: bool = is_blocked_on_0
        self.is_log: bool = is_log

    def get_jsonable(self) -> dict:
        """Marshal object to python dictionary

        Returns:
            dict: Dictionary ready to save as .json
        """
        jsonable: dict = {
         "name": self.name, 
         "symbol": self.symbol,
         "min": self.min,
         "max": self.max,
         "value": self.value,
         "error": self.error,
         "is_blocked": self.is_blocked,
         "is_log": self.is_log,
         "is_blocked_on_0": self.is_blocked_on_0
        }
        return jsonable

    def update_from_json(self, j: dict):
        """From given dictionary recreate saved state

        Args:
            j (dict): Result of self.get_jsonable()

        Examaples:
            >>> self.set_value(5)
            >>> d = self.get_jsonable()
            >>> self.set_value(99)
            >>> self.update_from_json(d)
            >>> print(self.get_value())
            5.0
        """
        self.name = j["name"] 
        self.symbol = j["symbol"]
        self.min = j["min"] 
        self.max = j["max"]
        self.value = j["value"]
        self.error = j["error"]
        self.is_blocked = j["is_blocked"]
        self.is_log = j["is_log"]
        self.is_blocked_on_0 = j["is_blocked_on_0"]

    def get_range(self) -> tuple[float, float]:
        """Return boundaries of parameter.

        Returns:
            tuple[float, float]: Minimal value, Maximal value
        """
        return (self.min, self.max)

    def set_value(self, v: float, silent: bool=False, new_error:float=0.0, emit_reset_errors=False):
        """Set parameter internal value to new one
        
        Args:
            v (float): New parameter value.
            silent (bool): Determines whether to emit value_changed signal.
        """
        if v < self.min:
            v = self.min

        if v > self.max:
            v = self.max

        self.value = v
        self.set_error(new_error)
        if not silent:
            self.value_changed.emit(v)
        if emit_reset_errors:
            self.reset_errors.emit(True)

    def get_value(self):
        """Get current parameter value

        Returns:
            float: Current parameter value
        """

        return self.value

    def set_error(self, v: float, silent=False):
        """Set new error value.

        Args:
            v (float): New error value
            silent (bool, optional): Determines whether to emit error_changed signal. Defaults to False.
        """
        self.error = v
        if not silent:
            self.error_changed.emit(v)

    def set_blocked(self, block: bool):
        """Set new blocked state. Emits blocked_state_change signal

        Args:
            block (bool): New block sate.
        """
        self.is_blocked = block
        self.block_state_changed.emit(self.is_blocked)

    def set_blocked_0(self, block: bool):
        """Set new blocked on 0 state. Emits blocked_0_state_change signal

        Args:
            block (bool): New block on 0 sate.
        """
        self.is_blocked_on_0 = block
        self.block_0_state_changed.emit(self.is_blocked_on_0)

    def set_range(self, min: float, max: float):
        self.min = min
        self.max = max
        self.set_value((max+min)/2.0, silent=False)
        self.range_changed.emit(self.name)
        
        
