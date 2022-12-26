from PyQt6.QtWidgets import QTreeView, QSizePolicy, QFrame, QAbstractScrollArea, QAbstractItemView
from PyQt6.QtGui import QStandardItem
from PyQt6.QtCore import pyqtSlot, Qt, QPoint
from models import ControlTreeModel
 

from controllers import ControlTreeController, CompoundItemsCollectionController
from models import CompoundItemsCollectionModel, ControlTreeModel
from .CompundItemsCollection import CompoundItemsCollection
from .StandardItem import StandardItem

class ControlTreeView(QTreeView):
    def __init__(self, working_space):
        super().__init__()
        self._model = ControlTreeModel(working_space)
        self._ctr = ControlTreeController(self._model)
        self.setModel(self._model)
        self.setObjectName("Control tree")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.setIndentation(10)
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        self.expandsOnDoubleClick()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_item_menu) # type: ignore
        self.clicked.connect(lambda index: self._model.itemFromIndex(index).on_click()) # type: ignore
        header = self.header()
        header.setDefaultSectionSize(250)
        header.setMinimumSectionSize(50)
        header.setStretchLastSection(True)
        header.setVisible(False)

        self.setAnimated(True)
        tree_model = CompoundItemsCollectionModel("relACs", self, self._model._working_space)
        self.compounds = CompoundItemsCollection(tree_model, CompoundItemsCollectionController(tree_model))
        rootNode:QStandardItem  = self.model().invisibleRootItem() # type: ignore
        rootNode.appendRow(self.compounds)
        self.expandAll()

    def show_item_menu(self, position: QPoint):
        item: StandardItem = self._model.itemFromIndex(self.indexAt(position))
        if item:
            item.show_menu(self.window().mapToGlobal(position))
