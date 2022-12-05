from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import FitItemsCollectionModel, Fit
from controllers import FitItemsCollectionController, FitItemController
from .StandardItem import StandardItem
from .FitItem import FitItem
class FitItemsCollection(StandardItem):
    def __init__(self, model: FitItemsCollectionModel, ctrl: FitItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model: FitItemsCollectionModel = model
        self._ctrl: FitItemsCollectionController = ctrl

        self._model.fit_added.connect(self.on_fit_added)
        self._model.fit_removed.connect(self.on_fit_removed)
        self._model.displayed_item_changed.connect(self.on_displayed_item_changed)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Make fit from all checked", self.parent().child(0).make_fits_checked)
        menu.exec(menu_position)

    def on_fit_added(self, new:Fit):
        self.appendRow(FitItem(new, FitItemController(new)))
        self._model.tree.expandAll()

    def on_displayed_item_changed(self, fit:Fit):
        self._model._compound._displayer.display_fit(fit)

    def on_fit_removed(self, index:QModelIndex):
        self.removeRow(index.row())

