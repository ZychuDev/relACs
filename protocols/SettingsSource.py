from typing import Protocol
from PyQt6.QtCore import pyqtSignal

class SettingsSource(Protocol):
    change_ranges: pyqtSignal
    def get_min(self, name: str) -> float:
        """Get lower boundry for given parameter name.

        Args:
            param_name (str): Name of the parameter.

        Returns:
            float: Lower boundry on parameter value.
        """
        ...

    def get_max(self, name: str) -> float:
        """Get upper boundry for given parameter name.

        Args:
            param_name (str): Parameter name.

        Returns:
            float: Upper boundry on parameter value.
        """
        ...

    def emit_change_ranges(self) -> None:
        """Emits chnage ranges signal
        """
        ...