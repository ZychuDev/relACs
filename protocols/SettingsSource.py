from typing import Protocol


from models import PARAMETER_NAME

class SettingsSource(Protocol):

    def get_min(self, name: PARAMETER_NAME) -> float:
        ...

    def get_max(self, name: PARAMETER_NAME) -> float:
        ...