from typing import Protocol

from models import Measurement, Fit, TauFit 
class Displayer(Protocol):

    def display_home_page(self): ...
    
    def display_measurement(self, measurement: Measurement): ...

    def display_fit(self, measurement: Fit): ...

    def display_tau_fit(self, measurement: TauFit): ...