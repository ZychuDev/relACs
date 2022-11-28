from PyQt6.QtWidgets import QStackedWidget

from models import Measurement, Fit, TauFit

from .HomePageView import HomePageView
from .DataExplorer import  DataExplorer

class WorkingSpace(QStackedWidget):
    def __init__(self):
        super().__init__()
        self._data_explorer:DataExplorer = DataExplorer()
        self._home_page: HomePageView = HomePageView()
        self._home_page_index = self.addWidget(self._home_page)
        self._data_explorer_index = self.addWidget(self._data_explorer)

    def display_home_page(self):
        self.setCurrentIndex(self._home_page_index)

    def display_measurement(self, model:Measurement):
        self._data_explorer.set_measurement(model)
        self.setCurrentIndex(self._data_explorer_index)

    def display_fit(self, model:Fit):
        pass

    def display_tau_fit(self, model:TauFit):
        pass