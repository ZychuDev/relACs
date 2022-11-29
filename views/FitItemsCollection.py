from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import FitItemsCollectionModel
from controllers import FitItemsCollectionController
from .StandardItem import StandardItem
from .FitItem import FitItem
class FitItemsCollection(StandardItem):
    def __init__(self, model: FitItemsCollectionModel, ctrl: FitItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model = model
        self._ctrl = ctrl


    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Make fit from all checked", self._ctrl.add_fit)
        menu.exec(menu_position)