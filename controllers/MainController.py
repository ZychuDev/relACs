from PyQt6.QtCore import QObject, pyqtSlot

from models.MainModel import MainModel

class MainController(QObject):
    def __init__(self, model:MainModel):
        self._model: MainModel = model

    @pyqtSlot(int)
    def change_amount(self, value):
        self._model.amount = value

        # calculate even or odd
        self._model.even_odd = 'odd' if value % 2 else 'even'

        # calculate button enabled state
        self._model.enable_reset = True if value else False