from PyQt6.QtCore import QObject, pyqtSlot
from models import FitItemsCollectionModel

class FitItemsCollectionController(QObject):
    def __init__(self, model:FitItemsCollectionModel):
        self._model = model

    def add_fit(self):
        print("Adding new measurement")