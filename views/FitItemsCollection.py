from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex, Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import FitItemsCollectionModel, Fit
from controllers import FitItemsCollectionController, FitItemController
from .StandardItem import StandardItem
from .FitItem import FitItem

from typing import Literal
from functools import partial

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
        submenu = menu.addMenu("Sort")
        submenu.addAction("Sort by temperature", partial(self.sort, "temp"))
        submenu.addAction("Sort by field", partial(self.sort, "field"))
        menu.addSeparator()

        menu.addAction("Check all", self.check_all)
        menu.addAction("Uncheck all", self.uncheck_all)
        menu.addSeparator()

        menu.addAction("Make auto fit for all checked", lambda: print("TO DO"))
        menu.addAction("Remove checked", self.remove_selected)
        menu.exec(menu_position)

    def on_fit_added(self, new:Fit):
        self.appendRow(FitItem(new, FitItemController(new)))
        self._model.tree.expandAll()

    def on_displayed_item_changed(self, fit:Fit):
        self._model._compound._displayer.display_fit(fit)
        print(fit.name)

    def on_fit_removed(self, index:QModelIndex):
        self.removeRow(index.row())

    def check_all(self):
        i: int
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.CheckState.Checked)

    def uncheck_all(self):
        i: int
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.CheckState.Unchecked)

    def sort(self, sort_by: Literal["temp", "field"]):
        self.sort_mode = sort_by

        i: int = 0
        while self.child(i) is not None:
            self.child(i).sort_mode = self.sort_mode # type: ignore
            i += 1

        self.sortChildren(0)

    def remove_selected(self):
        i: int = 0
        nr_of_rows: int = self.rowCount()
        while i < nr_of_rows:
            child = self.child(i)
            if child.checkState() == Qt.CheckState.Checked:
                self._model.remove(child._model._name, child.index())
                nr_of_rows -= 1
                i -= 1
            i += 1

