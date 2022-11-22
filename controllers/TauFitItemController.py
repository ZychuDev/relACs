from PyQt6.QtCore import QObject, pyqtSlot
from models import TauFit

class TauFitItemController(QObject):
    def __init__(self, model:TauFit):
        self._model = model