from PyQt6.QtCore import QObject, pyqtSlot
from models import TauFitItemsCollectionModel

class TauFitItemsCollectionController(QObject):
    def __init__(self, model:TauFitItemsCollectionModel):
        self._model = model

    def add_tau_fit(self):
        print("Adding new measurement")