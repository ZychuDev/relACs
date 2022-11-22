from PyQt6.QtCore import QObject, pyqtSlot
from models import Fit

class FitItemController(QObject):
    def __init__(self, model:Fit):
        self._model = model