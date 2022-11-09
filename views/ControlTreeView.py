from PyQt6.QtWidgets import QWidget, QTreeView, QSizePolicy, QFrame, QAbstractScrollArea, QAbstractItemView
from PyQt6.QtCore import pyqtSlot, Qt

class ControlTreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.setIndentation(10)
        self.setSortingEnabled(True)

        header = self.header()
        header.setDefaultSectionSize(250)
        header.setMinimumSectionSize(50)
        header.setStretchLastSection(True)

        self.setAnimated(True)
        