from PyQt6.QtCore import QObject, pyqtSlot
from models import MeasurementItemsCollectionModel

class MeasurementItemsCollectionController(QObject):
    def __init__(self, model:MeasurementItemsCollectionModel):
        self._model = model

    def add_measurement(self):
        print("Adding new measurement")