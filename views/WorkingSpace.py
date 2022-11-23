from PyQt6.QtWidgets import QStackedWidget

from models import Measurement, Fit, TauFit

from .HomePageView import HomePageView
from .DataExplorer import  DataExplorer

class WorkingSpace(QStackedWidget):
    def __init__(self):
        super().__init__()

        self._home_page_index = self.addWidget(HomePageView())
        self._data_explorer_index = self.addWidget(DataExplorer())

    def display_home_page(self):
        self.setCurrentIndex(self._home_page_index)

    def display_measurement(self, model:Measurement):
        self.setCurrentIndex(self._data_explorer_index)

    def display_fit(self, model:Fit):
        pass

    def display_tau_fit(self, model:TauFit):
        pass