from PyQt6.QtCore import pyqtSlot

from models import Compound
from controllers import CompoundItemController
from .StandardItem import StandardItem

class CompoundItem(StandardItem):
    def __init__(self, model: Compound, ctrl: CompoundItemController):
        super().__init__()
        self._model = model
        self._controller = ctrl

        self._model.name_changed.connect(self.on_name_changed)
        
    @pyqtSlot(str)
    def on_name_changed(self, new_name:str):
        self.setText(new_name)