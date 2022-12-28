from typing import Protocol

class SettingsSource(Protocol):

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