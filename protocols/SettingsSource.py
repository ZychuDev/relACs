from typing import Protocol

class SettingsSource(Protocol):

    def get_min(self, name: str) -> float:
        ...

    def get_max(self, name: str) -> float:
        ...