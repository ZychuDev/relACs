from typing import Protocol

from models import Measurement, Fit, TauFit
class Displayer(Protocol):

    def display_home_page(self):
        pass
    
    def display_measurement(self, measurement: Measurement):
        pass

    def display_fit(self, measurement: Fit):
        pass

    def display_tau_fit(self, measurement: TauFit):
        pass