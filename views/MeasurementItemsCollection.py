from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import MeasurementItemsCollectionModel
from controllers import MeasurementItemsCollectionController
from .StandardItem import StandardItem

class MeasurementItemsCollection(StandardItem):
    def __init__(self, model: MeasurementItemsCollectionModel, ctrl: MeasurementItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model: MeasurementItemsCollectionModel = model
        self._ctrl: MeasurementItemsCollectionController = ctrl

        self._model.name_changed.connect(lambda a,b: self.on_name_changed(a,b))
    
    @pyqtSlot(str)
    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Create new measurement", self._ctrl.add_measurement)
        menu.exec(menu_position)