from PyQt6.QtGui import QStandardItemModel
from .Compound import Compound

class ControlTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.compounds: list[Compound] = []