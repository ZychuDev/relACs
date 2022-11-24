from typing import Protocol
from PyQt6.QtCore import QModelIndex

class Collection(Protocol):

    def check_name(self, new_name:str) -> bool:
        pass

    def update_names(self, old_name: str, new_name:str):
        pass

    def remove(self, name: str, index: QModelIndex):
        pass