from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget
class WorkingSpaceModel(QObject):
    page_changed:pyqtSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._actual_page: str = ""
        self._pages: dict(str, QWidget) = {}

    def add_page(self, page_name:str, page:QWidget) -> None:
        for key in self._pages.keys():
            if key == page_name:
                raise KeyError(f"Page with name: {page_name} already exists.")
        self._pages.update({page_name: page})

    def change_page(self, page_name: str) -> None:
        if self._actual_page != page_name:
            self._actual_page = page_name
            self.page_changed.emit(page_name)
        




    