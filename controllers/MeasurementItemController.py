from PyQt6.QtCore import QObject, pyqtSlot
from models import Measurement
from protocols import Displayer

class MeasurementItemController(QObject):
    def __init__(self, model:Measurement):
        self._model = model
        
