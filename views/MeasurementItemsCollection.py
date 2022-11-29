from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex, Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu, QTreeView
from models import MeasurementItemsCollectionModel, Measurement
from controllers import MeasurementItemsCollectionController, MeasurementItemController

from .StandardItem import StandardItem
from .MeasurementItem import MeasurementItem

from typing import cast, Literal
from functools import partial

class MeasurementItemsCollection(StandardItem):
    def __init__(self, model: MeasurementItemsCollectionModel, ctrl: MeasurementItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model: MeasurementItemsCollectionModel = model
        self._ctrl: MeasurementItemsCollectionController = ctrl

        self.sort_mode: Literal["temp", "field"] = "temp"

        #self._model.name_changed.connect(self.on_name_changed)
        self._model.measurement_added.connect(self.on_measurement_added) 
        self._model.measurement_removed.connect(self.on_measurement_removed)
        self._model.displayed_item_changed.connect(self.on_displayed_item_changed)

    def on_click(self):
        pass

    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def on_measurement_added(self, new:Measurement):
        self.appendRow(MeasurementItem(new, MeasurementItemController(new)))
        self._model.tree.expandAll()

    def on_displayed_item_changed(self, measurement:Measurement):
        self._model._compound._displayer.display_measurement(measurement)

    def on_measurement_removed(self, index:QModelIndex):
        self.removeRow(index.row())

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Load measurements from file", self._ctrl.load_measurements_from_file)
        menu.addSeparator()
        
        submenu = menu.addMenu("Sort")
        submenu.addAction("Sort by temperature", partial(self.sort, "temp"))
        submenu.addAction("Sort by field", partial(self.sort, "field"))
        menu.addSeparator()

        menu.addAction("Check all", self.check_all)
        menu.addAction("Uncheck all", self.uncheck_all)
        menu.addSeparator()

        menu.addAction("Make fits from all loaded data", self.make_all_fits)
        menu.addAction("Make fits from checked data", self.make_fits_checked)
        menu.addAction("Make 2-relaxations fits from checked data", self.make_fits_checked_2)
        menu.addSeparator()

        menu.addAction("Remove checked", self.remove_selected)
        menu.exec(menu_position)

    def display_member(self, index: QModelIndex):
        measurement: Measurement = cast(Measurement, self.model().itemFromIndex(index))
        self._model._compound._displayer.display_measurement(measurement)

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

    def make_all_fits(self):
        pass

    def make_fits_checked(self):
        pass

    def make_fits_checked_2(self):
        pass