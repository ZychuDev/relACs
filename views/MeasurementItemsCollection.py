from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu, QTreeView

from models import MeasurementItemsCollectionModel, Measurement
from controllers import MeasurementItemsCollectionController, MeasurementItemController

from .StandardItem import StandardItem
from .MeasurementItem import MeasurementItem

class MeasurementItemsCollection(StandardItem):
    def __init__(self, model: MeasurementItemsCollectionModel, ctrl: MeasurementItemsCollectionController,
     tree:QTreeView):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model: MeasurementItemsCollectionModel = model
        self._ctrl: MeasurementItemsCollectionController = ctrl

        self._tree: QTreeView = tree
        self._model.name_changed.connect(self.on_name_changed)

    def on_click(self):
        self._ctrl.display()

    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def on_measurement_added(self, new:Measurement):
        self.appendRow(MeasurementItem(new, MeasurementItemController(new, self._model._compound._displayer)))
        self._tree.expandAll()
        self._model._compound._displayer.display_measurement(new)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Create new measurement", self._ctrl.add_measurement)
        menu.exec(menu_position)