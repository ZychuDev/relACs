from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import CompoundItemsCollectionModel
from controllers import CompoundItemsCollectionController
from .StandardItem import StandardItem

class CompoundItemsCollection(StandardItem):
    def __init__(self, model: CompoundItemsCollectionModel, ctrl: CompoundItemsCollectionController):
        super().__init__(model._name, model._font_size, model._set_bold)
        self.setBackground(QBrush(QColor(255,122,0)))
        self._model = model
        self._ctrl = ctrl

        self._model.name_changed.connect(lambda a,b: self.on_name_changed(a,b))
    
    @pyqtSlot(str)
    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def showMenu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Create new compound", self._ctrl.add_compound)
        menu.exec(menu_position)