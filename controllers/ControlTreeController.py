from PyQt6.QtCore import QModelIndex, QPoint
from models import ControlTreeModel

class ControlTreeController():
    def __init__(self, model:ControlTreeModel):
        self._model = model


