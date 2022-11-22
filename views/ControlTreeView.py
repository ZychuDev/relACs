from PyQt6.QtWidgets import QWidget, QTreeView, QSizePolicy, QFrame, QAbstractScrollArea, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtCore import pyqtSlot, Qt
from models import ControlTreeModel
from controllers import ControlTreeController

class ControlTreeView(QTreeView):
    def __init__(self):
        super().__init__()
        self._model = ControlTreeModel()
        self._ctr = ControlTreeController(self._model)
        self.setModel(self._model)
        self.setObjectName("Control tree")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setTextElideMode(Qt.TextElideMode.ElideLeft)
        self.setIndentation(10)
        self.setSortingEnabled(True)
        self.expandsOnDoubleClick()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda position: self._model.itemFromIndex(self.indexAt(position)).showMenu(self.window().mapToGlobal(position))) # type: ignore

        header = self.header()
        header.setDefaultSectionSize(250)
        header.setMinimumSectionSize(50)
        header.setStretchLastSection(True)
        header.setVisible(False)

        self.setAnimated(True)
        self.expandAll()


