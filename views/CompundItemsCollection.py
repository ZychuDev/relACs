from PyQt6.QtCore import pyqtSlot

from models import CompoundsCollection
from controllers import CompoundItemsCollectionController
from .StandardItem import StandardItem

class CompoundItemsCollection(StandardItem):
    def __init__(self, model: CompoundsCollection, ctrl: CompoundItemsCollectionController):
        super().__init__()
        self.setText(model._name)
        self._model = model
        self._controller = ctrl

        self._model.name_changed.connect(lambda a,b: self.on_name_changed(a,b))
    
    @pyqtSlot(str)
    def on_name_changed(self, new_name:str):
        self.setText(new_name)
