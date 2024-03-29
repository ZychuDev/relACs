from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtGui import QPalette
from PyQt6.QtCore import Qt

from models import Measurement, Fit, TauFit

from .HomePageView import HomePageView
from .DataExplorer import  DataExplorer
from .FitPage import FitPage
from .TauFitPage import TauFitPage

class WorkingSpace(QStackedWidget):
    """
        Space for visualization of current chosen item in :class: '.ControlTreeView'
    """
    def __init__(self):
        super().__init__()
        self._home_page: HomePageView = HomePageView()
        self._data_explorer: DataExplorer = DataExplorer()
        self._fit_page: FitPage = FitPage()
        self._tau_fit_page: TauFitPage = TauFitPage()

        self._home_page_index = self.addWidget(self._home_page)
        self._data_explorer_index = self.addWidget(self._data_explorer)
        self._fit_page_index = self.addWidget(self._fit_page)
        self._tau_fit_page_index = self.addWidget(self._tau_fit_page)

        p: QPalette = self.palette()
        p.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(p)
        self.setAutoFillBackground(True)

    def display_home_page(self):
        """
            Display home page
        """
        self.setCurrentIndex(self._home_page_index)

    def display_measurement(self, model:Measurement):
        """
            Set :class: 'Measurement' as current displayed item 
            and display measurement page.
        """
        self._data_explorer.set_measurement(model)
        self.setCurrentIndex(self._data_explorer_index)

    def display_fit(self, model:Fit):
        """
            Set :class: 'Fit' as current displayed item 
            and display fit page.
        """
        self._fit_page.set_fit(model)
        self.setCurrentIndex(self._fit_page_index)

    def display_tau_fit(self, model:TauFit):
       """
        Set :class: 'TauFit' as current displayed item 
        and display tau fit page.
       """
       self._tau_fit_page.set_tau_fit(model)
       self.setCurrentIndex(self._tau_fit_page_index)
