from PyQt6.QtCore import pyqtSlot

from PyQt6.QtGui import QColor, QBrush

from models import Measurement
from controllers import MeasurementItemController
from .StandardItem import StandardItem

class MeasurementItem(StandardItem):
    def __init__(self, model: Measurement, ctrl: MeasurementItemController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,255,255)))
        self.setCheckable(True)
        self._model: Measurement = model
        self._controller = ctrl

        self._model.name_changed.connect(self.on_name_changed)
        
    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def on_click(self):
        if self._model._collection.check_if_is_selected(self.index()):
            self._model._collection.change_displayed_item(self._model.name)