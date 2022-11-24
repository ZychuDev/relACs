from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu, QTreeView

from models import CompoundItemsCollectionModel, Compound, Measurement
from controllers import CompoundItemsCollectionController, CompoundItemController
from protocols import Displayer
from .StandardItem import StandardItem
from .CompoundItem import CompoundItem

class CompoundItemsCollection(StandardItem):

    def __init__(self, model: CompoundItemsCollectionModel, ctrl: CompoundItemsCollectionController, tree:QTreeView):
        super().__init__(model._name, model._font_size, model._set_bold)
        self.setBackground(QBrush(QColor(255,122,0)))
        self._model: CompoundItemsCollectionModel = model
        self._ctrl: CompoundItemsCollectionController = ctrl
        self._tree: QTreeView = tree
        # self._model.name_changed.connect(lambda a,b: self.on_name_changed(a,b))
        self._model.compound_added.connect(self.on_compound_added)
        self._model.compound_removed.connect(self.on_compound_removed)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Create new compound", self._ctrl.add_compound)    
        menu.exec(menu_position)

    def on_click(self):
        self._ctrl.display()

    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def on_compound_added(self, new:Compound):
        self.appendRow(CompoundItem(new, CompoundItemController(new)))
        self._tree.expandAll()
        self._model._displayer.display_measurement(Measurement("a", 12))

    def on_compound_removed(self, index:QModelIndex):
        self.removeRow(index.row())