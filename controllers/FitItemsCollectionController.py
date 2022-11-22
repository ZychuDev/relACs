from PyQt6.QtCore import QObject, pyqtSlot
from models import FitItemsCollectionModel

class FitItemsCollectionController(QObject):
    def __init__(self, model:FitItemsCollectionModel):
        super().__init__()
        self._model = model

    @pyqtSlot()
    def add_fit(self):
        print("Adding new measurement")