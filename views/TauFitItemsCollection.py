from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import TauFitItemsCollectionModel
from controllers import TauFitItemsCollectionController
from .StandardItem import StandardItem

class TauFitItemsCollection(StandardItem):
    def __init__(self, model: TauFitItemsCollectionModel, ctrl: TauFitItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model = model
        self._ctrl = ctrl


    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Save all to file", self._ctrl.add_tau_fit)
        menu.exec(menu_position)