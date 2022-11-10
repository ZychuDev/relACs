from PyQt6.QtCore import QObject, pyqtSlot
from models import Compound

class CompoundItemController(QObject):
    def __init__(self, model:Compound):
        self._model = model