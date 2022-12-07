from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QColor, QBrush

from models import Measurement
from controllers import MeasurementItemController
from .StandardItem import StandardItem

from typing import Literal
class MeasurementItem(StandardItem):
    def __init__(self, model: Measurement, ctrl: MeasurementItemController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,255,255)))
        self.setCheckable(True)
        self._model: Measurement = model
        self._ctrl: MeasurementItemController = ctrl

        self.sort_mode: Literal["temp", "field"] = "temp"

        self._model.name_changed.connect(self.on_name_changed)
        
    pyqtSlot(str)
    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def on_click(self):
        if self._model._collection.check_if_is_selected(self.index()):
            self._model._collection.change_displayed_item(self._model.name)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Rename", lambda: self._ctrl.rename())
        menu.addAction("Delete", lambda: self._model._collection.remove(self._model.name, self.index()))
        menu.exec(menu_position)

    def get_jsonable(self):
        jsonable: dict = self._model.get_jsonable()
        jsonable.update({"state": self.checkState(), "sort_mode": self.sort_mode})
        return jsonable
        
    def __lt__(self, other):
        if self.sort_mode == "temp":
            if self._model._tmp == other._model._tmp:
                return self._model._field < other._model._field
            return self._model._tmp < other._model._tmp

        if self.sort_mode == "field":
            if self._model._field == other._model._field:
                return self._model._tmp < other._model._tmp
            return self._model._field < other._model._field