from PyQt6.QtCore import pyqtSlot, QPoint
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu

from models import (
    Compound, MeasurementItemsCollectionModel,
    FitItemsCollectionModel, TauFitItemsCollectionModel)
from controllers import (
    CompoundItemController, MeasurementItemsCollectionController,
    FitItemsCollectionController, TauFitItemsCollectionController)

from .StandardItem import StandardItem
from .MeasurementItemsCollection import MeasurementItemsCollection
from .FitItemsCollection import FitItemsCollection
from .TauFitItemsCollection import TauFitItemsCollection

class CompoundItem(StandardItem):
    def __init__(self, model: Compound, ctrl: CompoundItemController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,255,255)))
        self.setCheckable(True)

        self._model: Compound = model
        self._ctrl: CompoundItemController = ctrl
        m_model = MeasurementItemsCollectionModel("Measurements")
        self.appendRow(MeasurementItemsCollection(m_model, MeasurementItemsCollectionController(m_model)))
        f1_model = FitItemsCollectionModel("Frequency Fits Single Relaxation")
        self.appendRow(FitItemsCollection(f1_model, FitItemsCollectionController(f1_model)))
        f2_model = FitItemsCollectionModel("Frequency Fits Double Relaxation")
        self.appendRow(FitItemsCollection(f2_model, FitItemsCollectionController(f2_model)))
        t_model = TauFitItemsCollectionModel("TauFits(3D)")
        self.appendRow(TauFitItemsCollection(t_model, TauFitItemsCollectionController(t_model)))
        self._model.name_changed.connect(self.on_name_changed)
        
    pyqtSlot(str)
    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Rename", lambda : self._ctrl.rename())
        menu.addAction("Delete", lambda : self._model._collection.remove(self._model.name, self.index()) )
        menu.exec(menu_position)

