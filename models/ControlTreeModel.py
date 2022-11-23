from PyQt6.QtGui import QStandardItemModel
from protocols import Displayer

class ControlTreeModel(QStandardItemModel):
    def __init__(self, working_space:Displayer):
        super().__init__()
        self._working_space: Displayer = working_space