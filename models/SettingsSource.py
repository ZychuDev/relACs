from typing_extensions import Protocol, runtime_checkable


from models import PARAMETER_NAME

@runtime_checkable
class SettingsSource(Protocol):

    def get_min(self, name: PARAMETER_NAME) -> float:
        ...

    def get_max(self, name: PARAMETER_NAME) -> float:
        ...