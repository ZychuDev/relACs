from typing import Protocol
from PyQt6.QtCore import QModelIndex
from .Displayer import Displayer

class Collection(Protocol):
    _displayer: Displayer
    
    def check_name(self, new_name:str) -> bool: ...

    def update_names(self, old_name: str, new_name:str) -> None: ...

    def remove(self, name: str, index: QModelIndex)-> None: ...

    def change_displayed_item(self, name: str) -> None: ...

    def check_if_is_selected(self, index: QModelIndex) -> bool: ...

    def get_next(self, name: str) -> str: ...

    def get_previous(self, name: str) -> str: ...

    def get_item_model(self, name: str): ...

    def get_names(self) -> list[str]: ...