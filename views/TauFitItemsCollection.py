from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import TauFitItemsCollectionModel, TauFit
from controllers import TauFitItemsCollectionController, TauFitItemController
from .TauFitItem import TauFitItem
from .StandardItem import StandardItem

class TauFitItemsCollection(StandardItem):
    def __init__(self, model: TauFitItemsCollectionModel, ctrl: TauFitItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model: TauFitItemsCollectionModel = model
        self._ctrl: TauFitItemsCollectionController = ctrl

        self._model.fit_added.connect(self.on_fit_added)
        self._model.fit_removed.connect(self.on_fit_removed)
        self._model.displayed_item_changed.connect(self.on_displayed_item_changed)



    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Save all to file", self._ctrl.add_tau_fit)
        menu.exec(menu_position)


    def on_displayed_item_changed(self, tau_fit:TauFit):
        self._model._compound._displayer.display_tau_fit(tau_fit)

    def on_fit_removed(self, index:QModelIndex):
        self.removeRow(index.row())

    def on_fit_added(self, new:TauFit):
        self.appendRow(TauFitItem(new, TauFitItemController(new)))
        self._model.tree.expandAll()

