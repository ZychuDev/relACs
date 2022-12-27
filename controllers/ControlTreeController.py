from PyQt6.QtCore import QModelIndex, QPoint
from PyQt6.QtGui import QStandardItemModel

class ControlTreeController():
    def __init__(self, model:QStandardItemModel):
        self._model = model


