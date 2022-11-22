from PyQt6.QtCore import QObject, pyqtSlot
from models import MeasurementItemsCollectionModel

class MeasurementsItemsCollectionController(QObject):
    def __init__(self, model:CompoundItemsCollectionModel):
        self._model = model

    def add_compound(self):
        print("Adding new measurement")