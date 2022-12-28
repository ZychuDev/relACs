from typing import Protocol
from PyQt6.QtCore import QModelIndex
from .Displayer import Displayer

class Collection(Protocol):
    _displayer: Displayer
    
    def check_name(self, new_name:str) -> bool: 
        """Check if item with given name is already in collection.

            Args:
                name (str): Item name.

            Returns:
                bool: If name is already taken.
        """
        ...

    def update_names(self, old_name: str, new_name:str) -> None:
        """Updates name register in collection.

        Args:
            old_name (str): Old item name.
            new_name (str): New item name.
        """
        ...

    def remove(self, name: str, index: QModelIndex)-> None: 
        """Remove item with given name from collection.

        Args:
            name (str): Name of item to remove.
            index (QModelIndex): Removed item's index in controll tree.
        """
        ...
    def change_displayed_item(self, name: str) -> None:
        """Replace currently displayed item.

        Args:
            name (str): Name of the item to display.
        """
        ...

    def check_if_is_selected(self, index: QModelIndex) -> bool:
        """Checks item select state.

        Args:
            index (QModelIndex): Item Index in cotroll tree.

        Returns:
            bool: Check state.
        """
        ...

    def get_next(self, name: str) -> str:
        """Get name of next item in collection.

        Args:
            name (str): Current item name.

        Returns:
            str: Next item name.
        """
        ...

    def get_previous(self, name: str) -> str:
        """Get name of previous item in collection.

        Args:
            name (str): Current item name.

        Returns:
            str: Previous item name.
        """
        ...

    def get_item_model(self, name: str):
        """Get item of given name

        Args:
            name (str): Name of item to retrieve.

        """
        ...

    def get_names(self) -> list[str]:
        """Get register of names

        Returns:
            set[str]: All names of collection elements.
        """
        ...