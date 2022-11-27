from PyQt6.QtCore import QObject, pyqtSlot
from models import Measurement
from protocols import Displayer

class MeasurementItemController(QObject):
    def __init__(self, model:Measurement, displayer: Displayer):
        self._model = model
        self._displayer = displayer
        
    def display(self):
        self._displayer.display_measurement(self)