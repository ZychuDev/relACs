from PyQt6.QtGui import QStandardItemModel

class ControlTreeModel(QStandardItemModel):
    def __init__(self, working_space):
        super().__init__()
        self._working_space = working_space