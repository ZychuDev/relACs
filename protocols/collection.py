from typing import Protocol
from PyQt6.QtCore import QModelIndex

class Collection(Protocol):

    def check_name(self, new_name:str) -> bool:
        ...

    def update_names(self, old_name: str, new_name:str):
        ...

    def remove(self, name: str, index: QModelIndex):
        ...

    def change_displayed_item(self, name: str):
        ...

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        ...

    def get_next(self, name: str) -> str:
        ...

    def get_previous(self, name: str) -> str:
        ...

    def get_item_model(self, name: str):
        ...

    def get_names(self) -> list[str]: 
        ...