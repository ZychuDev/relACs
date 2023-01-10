from protocols import Collection, SettingsSource
from PyQt6.QtCore import QModelIndex
class MockupCollection():
    def __init__(self) -> None:
        self.names: list[str] = []
        self.displayed_item = ""

    def check_name(self, new_name:str) -> bool: 
        return new_name in self.names

    def update_names(self, old_name: str, new_name:str) -> None:
        for i, n in enumerate(self.names):
            if old_name == n:
                self.names[i] = new_name

    def remove(self, name: str, index: QModelIndex)-> None: 
        self.names.remove(name)

    def change_displayed_item(self, name: str) -> None:
        self.displayed_item = name

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        return True

    def get_next(self, name: str) -> str:
        for i,n in enumerate(self.names):
            if n == name:
                if i == len(self.names):
                    return self.names[0]
                return self.names[i+1]
        raise KeyError

    def get_previous(self, name: str) -> str:
        for i,n in enumerate(self.names):
            if n == name:
                return self.names[i-1]
        raise KeyError

    def get_item_model(self, name: str):
        pass

    def get_names(self) -> list[str]:
        return self.names

class MockupSettingsSource():
    def get_min(self, name:str):
        return 0

    def get_max(self, name:str):
        return 100