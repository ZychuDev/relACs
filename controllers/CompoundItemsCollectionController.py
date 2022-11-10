from PyQt6.QtCore import QObject, pyqtSlot
from models import CompoundsCollection

class CompoundItemsCollectionController(QObject):
    def __init__(self, model:CompoundsCollection):
        self._model = model